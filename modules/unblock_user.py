from linebot.models import TextSendMessage
from decorators import rule
from util.chat_logger import ChatLogger

@rule.is_owner
@rule.is_not_blocked
def unblock(event, **kwargs):
    user_id = event.message.text.split(" ", 1)[1]
    chat_logger = ChatLogger()
    chat_logger.unblock_user(user_id)
    return TextSendMessage(text=f"User {user_id} has been unblocked")
