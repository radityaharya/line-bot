import logging
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import TextSendMessage


logger = logging.getLogger("line-bot")


def get_group_members_profile(event, **kwargs) -> TextSendMessage:
    """
    Get Group Members Profile
    """
    line_bot_api = kwargs["line_bot_api"]
    group_id = event.source.group_id

    members = []
    try:
        member_ids = line_bot_api.get_group_member_ids(group_id)
        for member_id in member_ids.member_ids:
            user_profile = line_bot_api.get_group_member_profile(group_id, member_id)
            members.append(user_profile)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
    members_string = ""
    for member in members:
        members_string += f"{member.display_name} ({member.user_id})\n"
    return TextSendMessage(text=members_string)


def echo(event, **kwargs) -> TextSendMessage:
    """
    Echo
    """
    message = event.message.text
    message = message.replace("echo", "")
    if len(message) > 1000:
        message = "Message too long"
    if len(message) < 2:
        return None
    message.strip()
    return TextSendMessage(text=message)
