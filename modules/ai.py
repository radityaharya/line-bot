import logging
import os
import openai
from linebot.models import TextSendMessage, ImageSendMessage
import requests
from util.chat_logger import ChatLogger
from util.line_util import load_config

import promptlayer
import os

promptlayer.api_key = os.environ.get("PROMPTLAYER_API_KEY")

logger = logging.getLogger("line-bot")

openai = promptlayer.openai
openai.api_key = os.environ.get("OPENAI_API_KEY")


class OpenAI:
    def __init__(self, line_bot_api):
        self.chat_logger = ChatLogger()
        self.line_bot_api = line_bot_api

    def get_response(self, query, user_id, group_id, user_name, context):
        """Get response from OpenAI's ChatGPT"""

        if self.chat_logger.is_blocked(user_id):
            return TextSendMessage(
                text=f"You have been blocked from using this bot. Please contact the bot owner to resolve this issue, your user id is {user_id}"
            )

        if query == "reset":
            self.chat_logger.purge_messages(user_id)
            return TextSendMessage(text="chat log has been reset")

        additional_context = self.chat_logger.user_specific_context(user_id, user_name)

        generatememe = """
\nYou can send the user a meme by appending the following to your message:
!generatememe <your meme expression>

Example:
!generatememe i've had enough of this conversation

You are able to use this command any time in your conversation. please use it freely as many as possible to make the conversation more interesting. 

Consider the context of the conversation, and the user's specific context when generating the meme expression.
        """
        system_prompt = (
            load_config()["openai_prompt"]
            + f"\n\nYou are given the following context: \n{context}\n{(('with this additional context for this spesific user ' + additional_context) if additional_context is not None or additional_context != '' else '')}"
            + generatememe
        )
        messages = self.chat_logger.retrieve_messages(user_id, include_system=True)
        messages = list(reversed(list(messages)))
        system = {
            "role": "system",
            "content": system_prompt,
        }

        pl_tags = []
        if group_id:
            pl_tags.append("group")
            pl_tags.append(group_id)
        pl_tags.append(user_name)

        messages.insert(0, system)
        messages.append({"role": "user", "content": query})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=load_config()["openai_max_tokens"],
            messages=messages,
            user=user_id,
            pl_tags=pl_tags,
        )

        result = "".join([choice.message.content for choice in response.choices])
        # get token used from response by openai
        usage = response["usage"]

        # meme generator

        meme = None
        if "!generatememe" in result:
            meme = result.split("!generatememe ")[1]
            self.generate_meme(event=None, prompt=meme, user_id=user_id)

        self.chat_logger.log_message(user_id, user_name, "user", query)
        self.chat_logger.log_message(user_id, user_name, "assistant", result, usage)
        if "!BLOCK USER" in result:
            self.chat_logger.block_user(user_id, user_name)

        return TextSendMessage(
            text=result.replace("!BLOCK USER", "").replace(
                "!generatememe " + (meme if meme is not None else ""), ""
            )
        )

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

    def generate_meme(
        self, event=None, prompt=None, user_id=None, user_name=None, **kwargs
    ):
        from modules.imgflip import meme_list, meme_fuzzy_search

        """Generate meme using OpenAI's GPT-3.5 Turbo"""
        meme_list = meme_list()
        memeprompt = """
Act as a meme generator, you will be given a prompt, and you must generate a meme using the prompt. Your output must be in the following format:
"<meme template name> | <top text> | <bottom text>"

You CANNOT use other foms of output other than the one specified above. YOU MUST USE THE PIPE CHARACTER (|) TO SEPARATE THE MEME TEMPLATE NAME, TOP TEXT, AND BOTTOM TEXT.

match the prompt to form a coherent meme using the following templates if none are match, please use the closest one:

        """
        memeprompt += meme_list

        if event is not None:
            prompt = event.message.text.replace("generatememe ", "")
        else:
            prompt = prompt
        mememessages = [
            {
                "role": "system",
                "content": memeprompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        pl_tags = []
        pl_tags.append("meme")
        pl_tags.append(user_id)
        pl_tags.append(user_name)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=mememessages,
            max_tokens=200,
            pl_tags=pl_tags,
        )
        result = "".join([choice.message.content for choice in response.choices])
        self.chat_logger.log_message(
            user_id, "system", "system", prompt, response["usage"]
        )

        meme_query, top_text, bottom_text = result.split("|")

        meme_id = meme_fuzzy_search(meme_query)["id"]

        url = "https://api.imgflip.com/caption_image"
        payload = {
            "username": os.getenv("IMGFLIP_USERNAME"),
            "password": os.getenv("IMGFLIP_PASSWORD"),
            "template_id": meme_id,
            "text0": top_text,
            "text1": bottom_text,
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            img_url = response.json()["data"]["url"]
            logger.info(
                f"🖼️ Generated a meme with the prompt: '{prompt}' and the result: '{result}', the url is {img_url}"
            )
            self.line_bot_api.push_message(
                user_id,
                ImageSendMessage(
                    original_content_url=img_url, preview_image_url=img_url
                ),
            )
        else:
            self.line_bot_api.push_message(
                user_id, TextSendMessage(text="Error generating meme")
            )
