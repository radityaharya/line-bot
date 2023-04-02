import os
import random
import praw as _praw
from linebot.models import ImageSendMessage
import os
import logging
from decorators.temp import clear as clear_temp

logger = logging.getLogger("line-bot")


@clear_temp
def get_random_image_from_subreddit(event, **kwargs):
    host = kwargs["line_host"]
    print("get_random_image_from_subreddit")
    text = event.message.text[7:]
    subreddit = text.split(" ")[0]
    print(subreddit)
    reddit = _praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent="peeepeepoopoo",
    )
    subreddit = reddit.subreddit(subreddit)
    try:
        posts = subreddit.hot(limit=100)
    except:
        return None
    random_posts = random.sample(list(posts), 10)
    for post in random_posts:
        if (
            post.url.endswith(".jpg")
            or post.url.endswith(".png")
            or post.url.endswith(".gif")
        ):
            url = post.url
            break
    else:
        logger.info("No image found")
        return None

    logger.info(f"Sending image from {url}")
    return ImageSendMessage(original_content_url=url, preview_image_url=url)
