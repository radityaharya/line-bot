import requests
from linebot.models import TextSendMessage


def match_img_tracemoe(image_path):
    r = requests.post(
        "https://api.trace.moe/search?anilistInfo&cutBorders",
        data=open(image_path, "rb"),
        headers={"Content-Type": "image/jpeg"},
    )
    if r.status_code == 200:
        data = r.json()
        if data["result"][0]["similarity"] < 0.89:
            return None
        message = ""
        anime = data["result"][0]["anilist"]
        message += f"Title: {anime['title']['romaji']}\n"
        message += f"Episode: {data['result'][0]['episode']}\n"
        message += f"Similarity: {data['result'][0]['similarity']}\n"
        message += f"Start: {data['result'][0]['from']}\n"
        message += f"End: {data['result'][0]['to']}\n"
        message += f"Video: {data['result'][0]['video']}\n"
    else:
        return None
    return TextSendMessage(text=message)
