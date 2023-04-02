import os
import multiprocessing
import time
import logging

logger = logging.getLogger("line-bot")


def clear_temp():
    time.sleep(10)
    logger.info("Clearing temp")
    if os.path.exists(".static/tmp"):
        for filename in os.listdir("./static/tmp"):
            os.remove(f"./static/tmp/{filename}")
            logger.info(f"Removed {filename}")


def clear(func):
    def wrapper(*args, **kwargs):
        p = multiprocessing.Process(target=clear_temp)
        p.start()
        return func(*args, **kwargs)

    return wrapper
