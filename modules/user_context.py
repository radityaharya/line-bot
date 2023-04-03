from linebot.models import TextSendMessage

from util.chat_logger import ChatLogger


def overwrite_user_context(event, **kwargs):
    """Overwrite user context"""
    user_id = event.source.user_id
    context = event.message.text.split(" ", 1)[1]
    chat_logger = ChatLogger()
    chat_logger.overwrite_user_specific_context(user_id, context)
    return TextSendMessage(text="User context has been overwritten")
