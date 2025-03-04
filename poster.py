import logging
from datetime import datetime
import json
import requests

from telebot import TeleBot

from enums import Endpoint, PostStatus
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger()


class Poster:
    def __init__(self, bot_token: str, general_channel_telegram_id: str):
        self.GENERAL_CHANNEL_TELEGRAM_ID = general_channel_telegram_id
        self.bot = TeleBot(token=bot_token)

    @staticmethod
    def get_full_posts(publish_datetime: datetime):
        restrict = {
            "publishDate": publish_datetime.date().strftime("%Y-%m-%d"),
            "publishTime": publish_datetime.time().replace(second=0).strftime("%H:%M:%S"),
            "status": PostStatus.AWAITS.value
        }
        response = requests.get(Endpoint.POST.value, params={"restrict": json.dumps(restrict)})
        result = response.json().get("result")
        error = response.json().get("error")

        if response.status_code == 200:
            if result:
                if result.get("total") > 0:
                    logger.info(f"Found {result.get('total')} posts for {publish_datetime.strftime('%Y-%m-%d %H:%M')}")
                    return result.get("responseList")

                else:
                    logger.debug(f"No posts found for {publish_datetime.strftime('%Y-%m-%d %H:%M')}")

            elif error:
                logger.error(f"Get posts request failed with error: {error}")

        else:
            logger.error(f"Get posts request failed with status code: {response.status_code}, error: {error}")

        return []

    @staticmethod
    def format_posts(posts):
        if not posts:
            return []

        formatted_posts = []
        for post in posts:
            formatted_posts.append({
                "id": post.get("id"),
                "message_id": post.get("messageId"),
                "group": post.get("groupTelegramId"),
                "with_pin": post.get("withPin"),
            })
            logger.debug(f"Post with id {post.get('id')} has been formatted")

        logger.debug(f"Formatted {len(posts)} posts")
        return formatted_posts

    def get_posts(self, publish_datetime: datetime):
        posts = self.get_full_posts(publish_datetime)
        formatted_posts = self.format_posts(posts)
        return formatted_posts

    def publish_to_group(self, group_id, message_id: int, with_pin: bool):
        message = self.bot.forward_message(chat_id=group_id, from_chat_id=self.GENERAL_CHANNEL_TELEGRAM_ID,
                                           message_id=message_id)
        if with_pin:
            self.bot.pin_chat_message(message.chat.id, message.message_id, disable_notification=True)

        logger.info(f"Post with message id {message_id} has been published to target group "
                    f"{'with' if with_pin else 'without'} pin")

    def publish(self, post):
        message_id = post.get("message_id")
        group_id = post.get("group")
        with_pin = post.get("with_pin")
        self.publish_to_group(group_id, message_id, with_pin)

    @staticmethod
    def set_status(post_id: int, status: PostStatus):
        body = {
            "id": post_id,
            "status": status.value
        }
        response = requests.put(f"{Endpoint.POST.value}", json=body)
        result = response.json().get("result")
        error = response.json().get("error")

        if response.status_code == 200:
            if result:
                logger.info(f"Post with id {post_id} has been set status as {status.value}")
                return result

            elif error:
                logger.error(f"Update post status request failed with error: {error}")

        else:
            logger.error(f"Update post status request failed with status code: {response.status_code}, error: {error}")
