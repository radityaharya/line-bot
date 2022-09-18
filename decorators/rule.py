from distutils.command.config import config
import json
from linebot.models import TextSendMessage
import logging
from util.line_util import load_config
logger = logging.getLogger("line-bot")


def is_owner(func):
    def is_owner_wrapper(*args, **kwargs):
        config = load_config()
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

    def is_not_blocked_wrapper(*args, **kwargs):
        config = load_config()
        event = args[0]
        user_id = event.source.user_id
        if user_id not in config["blocked_ids"]:
            logger.info("Not blocked command")
            return func(*args, **kwargs)
        else:
            logger.info("Blocked command")
            return None

    return is_not_blocked_wrapper
