import datetime
import logging
import os
import re

import dotenv
import pymongo
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    AudioMessage,
    AudioSendMessage,
    DatetimePickerAction,
    FileMessage,
    FlexSendMessage,
    ImageMessage,
    ImageSendMessage,
    LocationSendMessage,
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
    VideoSendMessage,
)
from rich.logging import RichHandler

import util.line_util as line_util
import util.mail_parser as mail_parser
from modules.ai import OpenAI
from modules.binus import get_forum_latest_post, get_next_schedule
from modules.delete_chat_context import delete_chat_context
from modules.imgflip import make_meme
from modules.line import echo
from modules.ping import ping
from modules.reddit import get_random_image_from_subreddit
from modules.tracemoe import match_img_tracemoe
from modules.unblock_user import unblock
from modules.user_context import overwrite_user_context
from util.mongo_log_handler import MongoLogHandler

dotenv.load_dotenv(override=True)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
HOST = os.environ.get("LINE_HOST")

LOGGER = logging.getLogger("line-bot")
LOGGER.setLevel(logging.INFO)

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

line_log = pymongo.MongoClient(os.environ.get("MONGO_URI"))["line-bot"]["line-log"]
LOGGER.addHandler(MongoLogHandler(line_log))
logging.getLogger("werkzeug").setLevel(logging.INFO)

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

ai = OpenAI(line_bot_api)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    config = line_util.load_config()
    user_id = event.source.user_id
    user_name, user_picture_url = line_util.get_user_profile(line_bot_api, user_id)
    group_id = None
    LOGGER.info(f"[MESSAGE] {user_name} ({user_id}): {event.message.text}")
    line_util.check_owner_config(event)

    user_config = line_util.user_config(event, line_bot_api=line_bot_api)

    prefix = ""
    if not isinstance(event.source, SourceUser):
        if not event.message.text.startswith(config["prefix"]):
            LOGGER.info("Prefix not found")
            group_id = event.source.group_id
            return
        event.message.text = event.message.text.replace(config["prefix"], "", 1)
        prefix = config["prefix"]

    event.message.text = line_util.sanitize_text(event.message.text)
    triggers = {
        "bye": [line_util.leave, "Leave the group"],
        "ping": [ping, "Ping the bot"],
        "schedule": [get_next_schedule, "Get next schedule from binusmaya"],
        "forum": [
            get_forum_latest_post,
            "Get latest unread posts from binusmaya forum",
        ],
        "reddit": [get_random_image_from_subreddit, "Get random image from subreddit"],
        "echo": [echo, "Echo the message"],
        "meme": [
            make_meme,
            f"Make a meme, usage: {prefix}meme <template:id or query>/<top text>/<bottom text>",
        ],
        "overwritectx": [
            overwrite_user_context,
            f"Overwrite user context used by the AI, usage: {prefix}overwritectx <new context>",
        ],
        "unblock": [unblock, "Unblock the user, usage: unblock <user id>"],
        "deletechatctx": [
            delete_chat_context,
            "Delete chat context used by the AI, usage: deletechatctx <number of messages to delete>",
        ],
        "generatememe": [
            ai.generate_meme,
            f"Generate a meme, usage: {prefix}generatememe <prompt>",
        ],
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
        context = f"""
username: {user_name}
datetime: {datetime.datetime.now().strftime("%A, %d %B %Y. %I:%M %p")}
        """
        response = ai.get_response(
            query=event.message.text,
            user_id=user_id,
            group_id=group_id,
            user_name=user_name,
            context=context,
        )

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
        try:
            LOGGER.info(f"[MESSAGE] 🤖bot (bot): {response.text}")
        except AttributeError:
            pass
        line_bot_api.reply_message(event.reply_token, response)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    user_id = event.source.user_id
    user_name, user_picture_url = line_util.get_user_profile(line_bot_api, user_id)
    LOGGER.info(f"[IMAGE] {user_name} ({user_id}): {event.message.id}")
    line_util.check_owner_config(event)

    if event.message.id:
        message_content = line_bot_api.get_message_content(event.message.id)
        # save image to local
        if not os.path.exists("images"):
            os.makedirs("images")
        with open(f"images/{event.message.id}.jpg", "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
    else:
        LOGGER.info("No image found")

    image_message_handlers = [match_img_tracemoe]
    for handler in image_message_handlers:
        response = handler(image_path=f"images/{event.message.id}.jpg")
        if response:
            break
    if not response:
        response = TextSendMessage(
            text=f"No Match Found using theses handlers: {f', '.join([i.__name__ for i in image_message_handlers])}"
        )
    os.remove(f"images/{event.message.id}.jpg")
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
        for m in e.error.details:
            LOGGER.error("  %s: %s" % (m.property, m.message))
    except InvalidSignatureError:
        abort(400)
    return "OK"


@app.route("/push", methods=["POST"])
def receive_flex():
    config = line_util.load_config()
    key = request.headers["SECRET_KEY"]
    if key != os.environ.get("SECRET_KEY"):
        return "Invalid key", 403
    else:
        # LOGGER.info(f"Received push request {request.headers}, {request.json}")
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
                "sms-otp",
                "mail-forward",
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
            elif data["type"] == "sms-otp":
                otp = re.search(r"\d{4,6}", data["content"]["text"])
                # TODO: make better filter
                if otp:
                    otp = otp.group(0)
                    line_bot_api.push_message(
                        data["to"], TextSendMessage(text=data["content"]["text"])
                    )
                    line_bot_api.push_message(
                        data["to"],
                        TextSendMessage(text=otp),
                    )
                else:
                    return "Invalid OTP message", 400
            elif data["type"] == "mail-forward":
                content = str(data["content"]["text"])
                sender, recipient, subject, text_content, urls = mail_parser.parse(
                    content
                )

                content = f"From: {sender}\nTo: {recipient}\nSubject: {subject}\n\n{text_content}, urls: {urls}"
                line_bot_api.push_message(data["to"], ai.parse_email(content))

            return "OK", 200
        except Exception as e:
            LOGGER.exception(e)
            return "Error: " + str(e), 500


@app.route("/health")
def health():
    return "OK"


@app.route("/forum-ping", methods=["POST"])
def forum_ping(event=None):
    key = request.headers["SECRET_KEY"]
    if key != os.environ.get("SECRET_KEY"):
        return "Invalid key", 403
    if request.headers["Content-Type"] != "application/json":
        return "Invalid content type", 400
    else:
        posts = get_forum_latest_post(event, line_bot_api=line_bot_api, line_host=HOST)
        return "OK", 200


def run(*kwargs):
    return app(*kwargs)
