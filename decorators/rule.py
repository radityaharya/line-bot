import json
from linebot.models import TextSendMessage
import logging
logger = logging.getLogger("line-bot")


def is_owner(func):
    with open("config.json", "r") as f:
        config = json.load(f)
    def is_owner_wrapper(*args, **kwargs):
        event = args[0]
        user_id = event.source.user_id
        if user_id == config["owner_id"]:
            logger.info("Owner command")
            return func(*args, **kwargs)
        else:
            logger.info("Not owner command")
            return TextSendMessage(text="You are not the owner")
    return is_owner_wrapper

def is_not_blocked(func):
    with open("config.json", "r") as f:
        config = json.load(f)
    def is_not_blocked_wrapper(*args, **kwargs):
        event = args[0]
        user_id = event.source.user_id
        if user_id not in config["blocked_ids"]:
            logger.info("Not blocked command")
            return func(*args, **kwargs)
        else:
            logger.info("Blocked command")
            return None
    return is_not_blocked_wrapper