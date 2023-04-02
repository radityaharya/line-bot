from linebot.models import TextSendMessage
from decorators import rule


@rule.is_owner
@rule.is_not_blocked
def ping(event, **kwargs):
    return TextSendMessage(text="pong")
