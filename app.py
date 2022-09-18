from asyncio.log import logger
import datetime
import json
import logging
from re import M
from sys import prefix
import threading
import os
import time

import dotenv
import pymongo
from rich.logging import RichHandler
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    AudioMessage,
    DatetimePickerAction,
    FileMessage,
    FlexSendMessage,
    ImageMessage,
    ImageSendMessage,
    MessageAction,
    MessageEvent,
    PostbackEvent,
    VideoSendMessage,
    AudioSendMessage,
    LocationSendMessage,
    QuickReply,
    QuickReplyButton,
    SourceGroup,
    SourceRoom,
    SourceUser,
    TextMessage,
    TextSendMessage,
    VideoMessage,
)

import util.line_util as line_util

from modules.ping import ping
from modules.binus import get_next_schedule
from modules.reddit import get_random_image_from_subreddit
from modules.line import echo
from modules.imgflip import make_meme
from util.mongo_log_handler import MongoLogHandler

dotenv.load_dotenv(override=True)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
HOST = os.environ.get("LINE_HOST")

LOGGER = logging.getLogger("line-bot")
LOGGER.setLevel(logging.DEBUG)

logging.basicConfig(
    level="INFO",
    format="%(funcName)s-> %(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True, show_path=False, markup=True, enable_link_path=True
        )
    ],
)

filehandler = logging.FileHandler("line.log")
filehandler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s"))
line_log = pymongo.MongoClient(os.environ.get("MONGO_URI"))["line-bot"]["line-log"]
LOGGER.addHandler(filehandler)
LOGGER.addHandler(MongoLogHandler(line_log))
logging.getLogger("werkzeug").setLevel(logging.INFO)

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"prefix": "!", "owner_id": "", "blocked_ids": []}
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    user_name, user_picture_url = line_util.get_user_profile(line_bot_api, user_id)
    LOGGER.info(f"[MESSAGE] {user_name} ({user_id}): {event.message.text}")
    line_util.check_owner_config(event)

    prefix = ""
    if not isinstance(event.source, SourceUser):
        if not event.message.text.startswith(config["prefix"]):
            LOGGER.info("Prefix not found")
            return
        event.message.text = event.message.text.replace(config["prefix"], "", 1)
        prefix = config["prefix"]
            
    event.message.text = line_util.sanitize_text(event.message.text)
    triggers = {
        "bye": [line_util.leave, "Leave the group"],
        "ping": [ping, "Ping the bot"],
        "schedule": [get_next_schedule, "Get next schedule from binusmaya"],
        "reddit": [get_random_image_from_subreddit, "Get random image from subreddit"],
        "echo": [echo, "Echo the message"],
        "meme": [make_meme, f"Make a meme, usage: {prefix}meme <template:id or query>/<top text>/<bottom text>"],
    }
    if event.message.text == "help":
        
        message = "Available commands:\n"
        for trigger, (func, desc) in triggers.items():
            message += f"{prefix}{trigger}: {desc}\n"
        return line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message)
        )

    for trigger in triggers:
        if event.message.text.startswith(trigger):
            response = triggers[trigger][0](
                event, line_bot_api=line_bot_api, line_host=HOST
            )
            break
    else:
        LOGGER.info("Command not found")
        response = TextSendMessage(text="No command found")

    if isinstance(
        response,
        (
            AudioMessage,
            DatetimePickerAction,
            FileMessage,
            FlexSendMessage,
            ImageMessage,
            ImageSendMessage,
            MessageAction,
            MessageEvent,
            PostbackEvent,
            QuickReply,
            QuickReplyButton,
            SourceGroup,
            SourceRoom,
            SourceUser,
            TextMessage,
            TextSendMessage,
            VideoMessage,
        ),
    ):
        line_bot_api.reply_message(event.reply_token, response)


@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE Webhook Callback
    """
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    LOGGER.debug(body)
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return "OK"


@app.route("/push", methods=["POST"])
def receive_flex():
    key = request.headers["SECRET_KEY"]
    if key != os.environ.get("SECRET_KEY"):
        return "Invalid key", 403
    if request.headers["Content-Type"] != "application/json":
        return "Invalid content type", 400
    else:
        try:
            data = request.json
            if data["to"] == "@me":
                data["to"] = config["owner_id"]
            message_types = [
                "text",
                "image",
                "video",
                "audio",
                "location",
                "file",
                "flex",
            ]

            if data["type"] not in message_types:
                return (
                    "Invalid message type, must be one of " + ", ".join(message_types),
                    400,
                )
            elif data["type"] == "text":
                line_bot_api.push_message(
                    data["to"], TextSendMessage(text=data["content"]["text"])
                )
            elif data["type"] == "flex":
                line_bot_api.push_message(
                    data["to"],
                    FlexSendMessage(
                        alt_text=data["content"]["alt_text"],
                        contents=data["content"]["contents"],
                    ),
                )
            elif data["type"] == "image":
                line_bot_api.push_message(
                    data["to"],
                    ImageSendMessage(
                        original_content_url=data["content"]["original_content_url"],
                        preview_image_url=data["content"]["preview_image_url"],
                    ),
                )
            elif data["type"] == "video":
                line_bot_api.push_message(
                    data["to"],
                    VideoSendMessage(
                        original_content_url=data["content"]["original_content_url"],
                        preview_image_url=data["content"]["preview_image_url"],
                    ),
                )
            elif data["type"] == "audio":
                line_bot_api.push_message(
                    data["to"],
                    AudioSendMessage(
                        original_content_url=data["content"]["original_content_url"],
                        duration=data["content"]["duration"],
                    ),
                )
            elif data["type"] == "location":
                line_bot_api.push_message(
                    data["to"],
                    LocationSendMessage(
                        title=data["content"]["title"],
                        address=data["content"]["address"],
                        latitude=data["content"]["latitude"],
                        longitude=data["content"]["longitude"],
                    ),
                )
            return "OK", 200
        except Exception as e:
            logger.exception(e)
            return "Error: " + str(e), 500


@app.route("/health")
def health():
    return "OK"


def run(*kwargs):
    return app(*kwargs)
