import logging
import os
import openai
from linebot.models import TextSendMessage
from util.chat_logger import ChatLogger

logger = logging.getLogger("line-bot")
openai.api_key = os.environ.get("OPENAI_API_KEY")


class OpenAI:
    def __init__(self):
        self.chat_logger = ChatLogger()
        self.prompt = os.environ.get("OPENAI_PROMPT") or ""

    def get_response(self, query, user_id):
        """Get response from OpenAI's ChatGPT"""
        if query == "reset":
            self.chat_logger.purge_messages(user_id)
            return TextSendMessage(text="chat log has been reset")

        messages = self.chat_logger.retrieve_messages(user_id, include_system=True)
        messages = list(reversed(list(messages)))
        system = {
            "role": "system",
            "content": self.prompt,
        }
        messages.insert(0, system)
        messages.append({"role": "user", "content": query})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=100,
            messages=messages,
        )

        result = "".join([choice.message.content for choice in response.choices])

        self.chat_logger.log_message(user_id, "user", query)
        self.chat_logger.log_message(user_id, "assistant", result)

        return TextSendMessage(text=result)

    def parse_email(self, email):
        """Parse email using OpenAI's GPT-3.5 Turbo"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "As an email assistant, your task is to analyze an email and provide the sender, recipient, subject, and content. Once you have this information, you must send it to the user as a text message also, send the url if present. Additionally, you need to check if the email is potentially spam.",
                },
                {"role": "user", "content": email},
            ],
            max_tokens=200,
        )
        result = "".join([choice.message.content for choice in response.choices])

        return TextSendMessage(text=result)
