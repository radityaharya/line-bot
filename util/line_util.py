
import json
from linebot.models import (
    SourceUser,
    SourceGroup,
    SourceRoom,
)
from linebot.exceptions import LineBotApiError
from linebot.models import (TextSendMessage)
import re
import logging
logger = logging.getLogger("line-bot")

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
        print("Got exception from LINE Messaging API: %s\n" % e.message)
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

def check_owner_config(event):
    """
    used in first time to set owner id
    """
    user_id = event.source.user_id
    with open("config.json") as f:
        config = json.load(f)
    if config["owner_id"] == "":
        with open("config.json", "w") as f:
            config["owner_id"] = user_id
            json.dump(config, f, indent=4)

def clean_url_params(url: str) -> str:
    """
    Remove url params
    """
    return re.sub(r"\?.*", "", url)

def sanitize_text(text: str) -> str:
    blacklist = ["<", ">", "&", "'", '"', "`", "$", "{", "}", "(", ")", ";", "&&", "||", "|", ">", "<", "!"]

    text = clean_url_params(text)

    for char in blacklist:
        text = text.replace(char, "")
    return text

