import os

import requests
from fuzzywuzzy import fuzz
from linebot.models import ImageSendMessage, TextSendMessage

def get_memes():
    url = "https://api.imgflip.com/get_memes"
    response = requests.get(url)
    return response.json()


def meme_fuzzy_search(search):
    memes = get_memes()
    memes = memes["data"]["memes"]
    memes = [{"name": meme["name"], "id": meme["id"]} for meme in memes]
    memes_and_score = []
    for meme in memes:
        score = fuzz.ratio(meme["name"], search)
        memes_and_score.append({"name": meme["name"], "id": meme["id"], "score": score})
    memes_and_score = sorted(memes_and_score, key=lambda x: x["score"], reverse=True)
    return memes_and_score[0]


def make_meme(event, **kwargs):
    input = event.message.text.split("/")
    meme_query = input[0]
    top_text = input[1]
    bottom_text = input[2]

    if meme_query.isdigit():
        meme_id = meme_query
    else:
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
        return ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
    else:
        return TextSendMessage(
            text=f"Something went wrong, status code: {response.status_code}, response: {response.json()}"
        )
