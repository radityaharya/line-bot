import logging
import os

import openai
from dotenv import load_dotenv
from linebot.models import TextSendMessage

logger = logging.getLogger("line-bot")


class OpenAI:
    def __init__(self):
        load_dotenv(override=True)
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def get_response(self, query):
        response = openai.completion.create(
            engine="davinci",
            prompt=query,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["\n", " Human:", " AI:"],
        )
        return response.choices[0].text

    def get_message(self, query):
        response = self.get_response(query)
        return TextSendMessage(text=response)

    def classify_message(self, categories: list, query: str) -> str:
        prompt_str = f"""valid categories = {", ".join(categories)}\ntext = "{query}"\nresult category = 
        """
        response = openai.Completion.create(
            model="text-babbage-001",
            prompt=prompt_str,
            temperature=0.7,
            max_tokens=10,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
        )

        res = (
            response.choices[0]
            .text.split("=")[-1]
            .strip()
            .replace('"', "")
            .replace(":", "")
            .replace(" ", "")
            .lower()
        )
        logger.info(f"Result: {res}")
        if res in categories:
            return res
        return None
