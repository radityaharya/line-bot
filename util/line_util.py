import json
import logging
import os
import re

import pymongo
from dotenv import load_dotenv
from linebot.exceptions import LineBotApiError
from linebot.models import SourceGroup, SourceRoom, SourceUser, TextSendMessage

logger = logging.getLogger("line-bot")
load_dotenv(override=True)
client = pymongo.MongoClient(os.environ.get("MONGO_URI"), maxPoolSize=50)


def get_user_profile(line_bot_api, uid: str) -> tuple:
    """
    Get User Profile
    """
    user_name = ""
    user_picture_url = ""
    try:
        user_profile = line_bot_api.get_profile(uid)
        user_name = user_profile.display_name
        user_picture_url = user_profile.picture_url
    except LineBotApiError as e:
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
    return user_name, user_picture_url


def leave(event, **kwargs):
    line_bot_api = kwargs["line_bot_api"]
    if isinstance(event.source, SourceGroup):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Leaving group")
        )
        line_bot_api.leave_group(event.source.group_id)
    elif isinstance(event.source, SourceRoom):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Leaving group")
        )
        line_bot_api.leave_room(event.source.room_id)
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Bot can't leave from 1:1 chat")
        )
    return "Leaving group"


def load_config() -> dict:
    """
    Load config from mongodb
    """

    config = client["line-bot"]["config"].find_one()
    if config is None:
        config = {
            "prefix": "!",
            "owner_id": "",
            "blocked_ids": [],
            "openai_prompt": "",
            "chat_context_limit": 50,
            "openai_max_tokens": 100,
        }
        logger.info(
            "config not found, creating new one, invoke first chat to set owner_id"
        )
        client["line-bot"]["config"].insert_one(config)
        config = client["line-bot"]["config"].find_one()
    logger.debug(f"config: {config}")
    return config


def check_owner_config(event):
    """
    used in first time to set owner id
    """
    user_id = event.source.user_id
    config = load_config()

    # check if "OWNER_ID" is set in env
    if "OWNER_ID" in os.environ:
        if config["owner_id"] == "":
            client["line-bot"]["config"].update_one(
                {}, {"$set": {"owner_id": os.environ["OWNER_ID"]}}
            )
            logger.info("Owner ID set to " + os.environ["OWNER_ID"])
        return

    if config["owner_id"] == "":
        client["line-bot"]["config"].update_one({}, {"$set": {"owner_id": user_id}})
        logger.info("Owner ID set to " + user_id)


def user_config(event=None, user_id=None, **kwargs):
    """
    Get user config
    """
    if event is not None:
        user_id = event.source.user_id
    if kwargs.get("line_bot_api") is not None:
        line_bot_api = kwargs.get("line_bot_api")
        user_name, user_picture_url = get_user_profile(line_bot_api, user_id)
    else:
        user_name = ""
        user_picture_url = ""
    config = client["line-bot"]["user-config"].find_one({"user_id": user_id})
    if config is None:
        config = {
            "user_id": user_id,
            "user_name": user_name,
            "user_picture_url": user_picture_url,
            "user_context": "",
            "is_blocked": False,
            "is_admin": False,
        }
        client["line-bot"]["user-config"].insert_one(config)
        config = client["line-bot"]["user-config"].find_one({"user_id": user_id})
    return config


def clean_url_params(url: str) -> str:
    """
    Remove url params
    """
    return re.sub(r"\?.*", "", url)


def sanitize_text(text: str) -> str:
    blacklist = [
        "<",
        ">",
        "&",
        "'",
        '"',
        "`",
        "$",
        "{",
        "}",
        "(",
        ")",
        ";",
        "&&",
        "||",
        "|",
        ">",
        "<",
        "!",
    ]

    text = clean_url_params(text)

    for char in blacklist:
        text = text.replace(char, "")
    return text
