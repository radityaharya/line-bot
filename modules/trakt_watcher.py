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
import pymongo

client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

db = client["line-bot"]
posted = db["trakt-posted"]
last_run = db["last-run"]

load_dotenv(override=True)

logger = logging.getLogger("line-bot")


def watcher(OFFSET_DAYS=0):
    logger.info("Starting Trakt Watcher")
    trakt_last_run = None
    # get the last run from db
    for doc in last_run.find():
        if doc["name"] == "trakt":
            trakt_last_run = doc["last_run"]

    if trakt_last_run is None:
        last_run.insert_one({"name": "trakt", "last_run": datetime.datetime.now()})

    if (
        trakt_last_run is not None
        and datetime.datetime.now() - trakt_last_run < datetime.timedelta(hours=1)
    ):
        logger.info("Last run was less than 1 hour ago, skipping")
        return

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
                if posted.find_one({"title": data["title"], "season": data["season"], "episode": data["episode"]}) is None:
                    logger.info(
                        f"{episode.show} episode {episode.episode} has not been posted"
                    )
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
                    r = requests.post(
                        endpoint,
                        json=json_data,
                        headers={
                            "Content-Type": "application/json",
                            "SECRET_KEY": os.environ.get("SECRET_KEY"),
                        },
                    )
                    r.close()
                    posted.insert_one(data)
        last_run.update_one(
            {"name": "trakt"}, {"$set": {"last_run": datetime.datetime.now()}}
        )
        time.sleep(10)
