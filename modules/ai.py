import logging
import os
import openai
from linebot.models import TextSendMessage
from util.chat_logger import ChatLogger
from util.line_util import load_config

logger = logging.getLogger("line-bot")
openai.api_key = os.environ.get("OPENAI_API_KEY")


class OpenAI:
    def __init__(self):
        self.chat_logger = ChatLogger()

    def get_response(self, query, user_id, user_name, context):
        """Get response from OpenAI's ChatGPT"""

        if self.chat_logger.is_blocked(user_id):
            self.chat_logger.log.update_one(
                {"type": "block", "user_id": user_id},
                {"$inc": {"chat_after_block_count": 1}},
            )

            if (
                self.chat_logger.log.find_one({"type": "block", "user_id": user_id})[
                    "chat_after_block_count"
                ]
                > 5
            ):
                return None

            return TextSendMessage(
                text=f"You have been blocked from using this bot. Please contact the bot owner to resolve this issue, your user id is {user_id}"
            )

        if query == "reset":
            self.chat_logger.purge_messages(user_id)
            return TextSendMessage(text="chat log has been reset")

        additional_context = self.chat_logger.user_specific_context(user_id, user_name)

        system_prompt = (
            load_config()["openai_prompt"]
            + f"\n\nYou are given the following context: \n{context}\n{(('with this additional context for this spesific user ' + additional_context) if additional_context is not None or additional_context != '' else '')}"
        )
        print(system_prompt)

        messages = self.chat_logger.retrieve_messages(user_id, include_system=True)
        messages = list(reversed(list(messages)))
        system = {
            "role": "system",
            "content": system_prompt,
        }
        messages.insert(0, system)
        messages.append({"role": "user", "content": query})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=load_config()["openai_max_tokens"],
            messages=messages,
            user=user_id,
        )

        result = "".join([choice.message.content for choice in response.choices])
        # get token used from response by openai
        usage = response["usage"]

        self.chat_logger.log_message(user_id, user_name, "user", query)
        self.chat_logger.log_message(user_id, user_name, "assistant", result, usage)
        if "!BLOCK USER" in result:
            self.chat_logger.block_user(user_id, user_name)

        return TextSendMessage(text=result.replace("!BLOCK USER", ""))

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
