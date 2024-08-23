import logging
from time import sleep as sl
from datetime import datetime

from enums import PostStatus
from poster import Poster
from config_reader import config
from logging_config import setup_logging


setup_logging()
logger = logging.getLogger()


def sleep(seconds: int):
    logger.debug(f"Sleeping for {seconds} seconds")
    sl(seconds)


def main():
    poster = Poster(config.BOT_TOKEN.get_secret_value(), config.GENERAL_CHANNEL_TELEGRAM_ID)

    while True:
        now = datetime.now()
        if now.minute == 0 or now.minute == 30 or True:
            logger.debug(f"Start publishing")
            try:
                posts = poster.get_posts(now)

                for post in posts:
                    try:
                        message_id = poster.publish(post)
                        logger.info(f"Post with id {post.get('id')} published")

                        poster.set_message_id(post.get("id"), message_id)
                        poster.set_status(post.get("id"), PostStatus.PUBLISHED)

                    except Exception as ex:
                        logger.error(f"Error publishing post {post}: {ex}")
                        poster.set_status(post.get("id"), PostStatus.ERROR)

            except Exception as ex:
                logger.error(f"Error: {ex}")

            sleep(60)

        else:
            sleep(30)


if __name__ == '__main__':
    main()
