import datetime
import logging
import time
import os
import requests
import trakt
from dotenv import load_dotenv
from flex_templates import trakt_template
from trakt.calendar import MyShowCalendar
from trakt.users import User
from util import tmdb_util

load_dotenv(override=True)

logger = logging.getLogger("line-bot")


def watcher(OFFSET_DAYS=0):
    logger.info("Starting Trakt Watcher")
    trakt_last_run = None
    try:
        with open("trakt_last_run.txt", "r") as f:
            trakt_last_run = f.readlines()[-1]
    except:
        with open("trakt_last_run.txt", "w") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if trakt_last_run is not None:
        datetime_last_run = datetime.datetime.strptime(
            trakt_last_run, "%Y-%m-%d %H:%M:%S"
        )
        if datetime_last_run > datetime.datetime.now() - datetime.timedelta(minutes=50):
            logger.info("Watcher already running")
            return
    with open("trakt_last_run.txt", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    trakt.core.CONFIG_PATH = "./trakt_config.json"
    me = User("otied")
    while True:
        episodes = MyShowCalendar(
            days=10, extended="full", date=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        for episode in episodes:
            data = {
                "title": episode.show,
                "episode": episode.episode,
                "season": episode.season,
                "airs_at": episode.airs_at,
                "tmdb_id": episode.show_data.tmdb,
                "tmdb_show_data": tmdb_util.tmdb_show_data(episode.show_data.tmdb),
                "tmdb_episode_data": tmdb_util.tmdb_episode_data(
                    episode.show_data.tmdb, episode.season, episode.episode
                ),
                "tmdb_episode_image": tmdb_util.tmdb_images(
                    episode.show_data.tmdb, episode.season, episode.episode
                ),
            }
            if episode.airs_at.date() == datetime.date.today() + datetime.timedelta(
                days=OFFSET_DAYS
            ):
                with open("posted_trakt.log", "r") as f:
                    posted_trakt = f.read()

                log_str = f"{data['title']} S{data['season']}E{data['episode']}"
                if log_str in posted_trakt:
                    logger.info(f"Already posted {log_str}")
                    continue

                contents = trakt_template(
                    title=data["title"],
                    episode=data["episode"],
                    season=data["season"],
                    alt_text="New episode of " + data["title"] + " airs today!",
                    img_url=data["tmdb_episode_image"],
                )

                endpoint = os.environ.get("LINE_HOST") + "/flex"
                json_data = {
                    "alt_text": "New episode of " + data["title"] + " airs today!",
                    "contents": contents,
                    "to": "@me",
                }
                logger.info(
                    "Sending message to {endpoint} with data {data}".format(
                        endpoint=endpoint, data=json_data
                    )
                )
                res = requests.post(
                    endpoint,
                    json=json_data,
                    headers={
                        "Content-Type": "application/json",
                        "SECRET_KEY": "peepeepoopoo",
                    },
                )
                logger.info(res.text)
                with open("posted_trakt.log", "a") as f:
                    # write to log with newline
                    f.write(log_str + "\n")
                # time.sleep(60)

        time.sleep(60)
