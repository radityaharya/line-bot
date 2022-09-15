import json
from lzma import FILTER_X86
from linebot.models import (
    FlexSendMessage,
)


def scheduleTemplate(
    header, title, session, start, end, kelas, topic, subtopic, link, location
):
    with open("schedule_config.json", "r") as f:
        colors = json.load(f)

    color = colors[title]

    flex_message = FlexSendMessage(
        alt_text="Class is about to start",
        contents={
            "type": "bubble",
            "size": "kilo",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": header,
                                "color": "#ffffff66",
                                "size": "sm",
                            },
                            {
                                "type": "text",
                                "text": title,
                                "color": "#ffffff",
                                "size": "xl",
                                "flex": 1,
                                "weight": "bold",
                                "wrap": True,
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "md",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": session,
                                        "color": "#F0F0F0",
                                        "size": "sm",
                                        "flex": 5,
                                    }
                                ],
                            },
                        ],
                        "spacing": "sm",
                    }
                ],
                "paddingAll": "20px",
                "backgroundColor": color,
                "spacing": "md",
                "paddingTop": "22px",
                "flex": 1,
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "none",
                        "spacing": "xs",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "none",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Class",
                                        "color": "#aaaaaa",
                                        "size": "xxs",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": kelas,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "xs",
                                        "flex": 5,
                                        "weight": "bold",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "none",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Time",
                                        "color": "#aaaaaa",
                                        "size": "xxs",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": start + "-" + end,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "xs",
                                        "flex": 5,
                                        "weight": "bold",
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "none",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Location",
                                        "color": "#aaaaaa",
                                        "size": "xxs",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": location,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "xs",
                                        "flex": 5,
                                        "weight": "bold",
                                    },
                                ],
                            },
                        ],
                    },
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "none",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Topic",
                                        "color": "#aaaaaa",
                                        "size": "xxs",
                                        "flex": 2,
                                        "weight": "regular",
                                    },
                                    {
                                        "type": "text",
                                        "text": topic,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "xs",
                                        "flex": 5,
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "none",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Subtopic",
                                        "color": "#aaaaaa",
                                        "size": "xxs",
                                        "flex": 2,
                                    },
                                    {
                                        "type": "text",
                                        "text": subtopic,
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "xs",
                                        "flex": 5,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "none",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "Link",
                            "uri": link,
                        },
                        "color": color,
                    }
                ],
                "flex": 0,
            },
        },
    )
    return flex_message


def trakt_template(
    title: str, season: int, episode: int, alt_text: str, img_url:str = None
):
    contents={
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": img_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "New Episode", "size": "sm"},
                    {
                        "type": "text",
                        "text": title,
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True,
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "spacing": "none",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Season",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1,
                                        "weight": "bold",
                                    },
                                    {
                                        "type": "text",
                                        "text": str(season),
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 1,
                                    },
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "Episode",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 1,
                                        "weight": "bold",
                                    },
                                    {
                                        "type": "text",
                                        "text": str(episode),
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "sm",
                                        "flex": 1,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        }
    flex_message = FlexSendMessage(
        alt_text=alt_text,
        contents=contents,
    )
    
    return contents
