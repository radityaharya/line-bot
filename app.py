import json
import logging
from multiprocessing import Process
import os

import dotenv
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
LOGGER.addHandler(filehandler)

logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

with open("config.json") as f:
    config = json.load(f)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    user_name, user_picture_url = line_util.get_user_profile(line_bot_api, user_id)
    LOGGER.info(f"[MESSAGE] {user_name} ({user_id}): {event.message.text}")
    line_util.check_owner_config(event)

    if not isinstance(event.source, SourceUser):
        if not event.message.text.startswith("!"):
            LOGGER.info("Prefix not found")
            return
        event.message.text = event.message.text.replace(config["prefix"], "", 1)

    event.message.text = line_util.sanitize_text(event.message.text)
    triggers = {
        "bye": line_util.leave,
        "ping": ping,
        "schedule": get_next_schedule,
        "reddit": get_random_image_from_subreddit,
        "echo": echo,
    }
    if event.message.text == "help":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="Available commands:\n- " + "\n- ".join(triggers.keys())
            ),
        )

    for trigger in triggers:
        if event.message.text.startswith(trigger):
            response = triggers[trigger](
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

@app.route("/health")
def health():
    return "OK"