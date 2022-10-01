import json
import re
from datetime import datetime
from lzma import FILTER_X86

from linebot.models import FlexSendMessage


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
    title: str, season: int, episode: int, alt_text: str, img_url: str = None
):
    season_episode = f"S{season:02d}E{episode:02d}"
    contents = {
        "type": "bubble",
        "size": "micro",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "image",
                            "url": img_url,
                            "size": "full",
                            "aspectRatio": "1:1.1",
                            "gravity": "center",
                            "flex": 1,
                            "aspectMode": "cover",
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "NEW EPISODE",
                                    "size": "10px",
                                    "color": "#ffffff",
                                    "align": "center",
                                    "gravity": "center",
                                }
                            ],
                            "backgroundColor": "#EC3D44",
                            "paddingAll": "2px",
                            "paddingStart": "4px",
                            "paddingEnd": "4px",
                            "flex": 0,
                            "position": "absolute",
                            "offsetStart": "10px",
                            "offsetTop": "10px",
                            "cornerRadius": "100px",
                            "width": "80px",
                            "height": "20px",
                        },
                    ],
                }
            ],
            "paddingAll": "0px",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "contents": [],
                                    "size": "md",
                                    "wrap": True,
                                    "text": title,
                                    "color": "#FFFFFF",
                                    "weight": "bold",
                                },
                                {
                                    "type": "text",
                                    "contents": [],
                                    "size": "xs",
                                    "wrap": True,
                                    "text": season_episode,
                                    "color": "#FFFFFF",
                                    "weight": "regular",
                                },
                            ],
                            "spacing": "sm",
                        }
                    ],
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": "#282828",
            "borderColor": "#282828",
        },
        "styles": {
            "header": {"separatorColor": "#282828"},
            "hero": {"separatorColor": "#282828"},
            "body": {"separatorColor": "#282828", "backgroundColor": "#282828"},
            "footer": {"separatorColor": "#282828", "backgroundColor": "#282828"},
        },
    }
    return contents


def forum_template(
    title: str,
    course: str,
    post_content: str,
    author_name: str,
    author_picture_url: str,
    post_datetime: datetime,
    post_url: str,
) -> FlexSendMessage:

    with open("schedule_config.json", "r") as f:
        colors = json.load(f)

    color = colors[course]

    post_datetime = post_datetime.strftime("%A, %d %B %Y %I:%M %p")

    contents = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": course,
                    "color": "#ffffff",
                    "align": "start",
                    "size": "xs",
                    "gravity": "center",
                    "margin": "lg",
                    "wrap": True,
                    "offsetTop": "0px",
                    "offsetBottom": "0px",
                },
                {
                    "type": "text",
                    "text": title,
                    "color": "#ffffff",
                    "align": "start",
                    "size": "md",
                    "gravity": "center",
                    "wrap": True,
                    "weight": "bold",
                },
                {
                    "type": "text",
                    "text": post_datetime,
                    "color": "#f0f0f0",
                    "align": "start",
                    "size": "xs",
                    "gravity": "center",
                    "margin": "sm",
                    "wrap": True,
                    "offsetTop": "0px",
                },
            ],
            "backgroundColor": color,
            "paddingTop": "19px",
            "paddingAll": "12px",
            "paddingBottom": "16px",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "image",
                                    "url": author_picture_url,
                                    "size": "xxs",
                                    "aspectMode": "cover",
                                    "align": "start",
                                }
                            ],
                            "cornerRadius": "xxl",
                            "justifyContent": "flex-start",
                            "alignItems": "flex-start",
                            "margin": "0px",
                            "spacing": "0px",
                            "flex": 0,
                        },
                        {
                            "type": "text",
                            "text": author_name,
                            "color": "#8C8C8C",
                            "size": "xxs",
                            "wrap": True,
                        },
                    ],
                    "flex": 1,
                    "alignItems": "center",
                    "spacing": "10px",
                    "margin": "0px",
                    "justifyContent": "flex-start",
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": post_content,
                            "wrap": True,
                        }
                    ],
                },
            ],
            "spacing": "md",
            "paddingAll": "12px",
            "action": {"type": "uri", "label": "action", "uri": post_url},
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [],
            "spacing": "10px",
        },
        "styles": {"footer": {"separator": False}},
    }

    # find valid urls in post_content
    urls = re.findall(r"(https?://\S+)", post_content)
    urls = [url.split("\\n")[0] for url in urls]

    for url in urls:
        contents["footer"]["contents"].append(
            {
                "type": "button",
                "action": {"type": "uri", "label": url, "uri": url},
                "height": "sm",
                "style": "primary",
                "color": color,
            }
        )

    alt_text = f"New post in {course}: {title}"
    return FlexSendMessage(alt_text=alt_text, contents=contents)
