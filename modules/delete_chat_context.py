from util.chat_logger import ChatLogger
from linebot.models import TextSendMessage


def delete_chat_context(event, **kwargs):
    """Delete chat context"""
    user_id = event.source.user_id
    number_of_messages = event.message.text.split(" ", 1)[1]
    chat_logger = ChatLogger()
    chat_logger.delete_n_number_of_messages(user_id, int(number_of_messages))
    return TextSendMessage(text="Chat context has been deleted")
