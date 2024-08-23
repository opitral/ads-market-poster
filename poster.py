import logging
from datetime import datetime
import json

import requests
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from enums import Endpoint, PostStatus, PublicationStatus
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger()


class Poster:
    def __init__(self, bot_token: str, general_channel_telegram_id: str):
        self.GENERAL_GROUP_TELEGRAM_ID = general_channel_telegram_id
        self.bot = TeleBot(token=bot_token)

    @staticmethod
    def get_posts_by_datetime(publish_datetime: datetime):
        restrict = json.dumps(
            {
                "publishDate": publish_datetime.date().strftime("%Y-%m-%d"),
                "publishTime": publish_datetime.time().replace(second=0).strftime("%H:%M:%S"),
                "status": PostStatus.AWAITS.value
            }
        )
        response = requests.get(Endpoint.POST.value, params={"restrict": restrict})
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
    def formatter(posts):
        if not posts:
            return

        formatted_posts = []
        for post in posts:
            formatted_posts.append({
                "id": post.get("id"),
                "publication": post.get("publication"),
                "group": post.get("groupTelegramId")
            })
            logger.debug(f"Post with id {post.get('id')} has been formatted")

        logger.debug(f"Formatted {len(posts)} posts")
        return formatted_posts

    def get_posts(self, publish_datetime: datetime):
        posts = self.get_posts_by_datetime(publish_datetime)
        formatted_posts = self.formatter(posts)
        return formatted_posts

    def publish_to_general_group(self, post):
        publication = post.get("publication")
        publication_type = publication.get("type")
        publication_file_id = publication.get("fileId")
        publication_text = publication.get("text")
        button = publication.get("button")

        keyboard = None
        if button:
            button_name = button.get("name")
            button_url = button.get("url")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text=button_name, url=button_url))

        if publication_type == PublicationStatus.TEXT.value:
            message = self.bot.send_message(self.GENERAL_GROUP_TELEGRAM_ID, publication_text, reply_markup=keyboard)

        elif publication_type == PublicationStatus.PHOTO.value:
            message = self.bot.send_photo(self.GENERAL_GROUP_TELEGRAM_ID, photo=publication_file_id,
                                          caption=publication_text, reply_markup=keyboard)

        elif publication_type == PublicationStatus.VIDEO.value:
            message = self.bot.send_video(self.GENERAL_GROUP_TELEGRAM_ID, video=publication_file_id,
                                          caption=publication_text, reply_markup=keyboard)

        elif publication_type == PublicationStatus.ANIMATION.value:
            message = self.bot.send_animation(self.GENERAL_GROUP_TELEGRAM_ID, animation=publication_file_id,
                                              caption=publication_text, reply_markup=keyboard)

        else:
            error = f"Unknown publication type: {publication_type}"
            logger.error(error)
            raise ValueError(error)

        logger.info(f"Post with id {post.get('id')} has been published to general group")
        return message.message_id

    def publish_to_group(self, group_id,  message_id):
        self.bot.forward_message(chat_id=group_id, from_chat_id=self.GENERAL_GROUP_TELEGRAM_ID, message_id=message_id)
        logger.info(f"Post with message id {message_id} has been published to target group")

    def publish(self, post):
        group_id = post.get("group")
        message_id = self.publish_to_general_group(post)
        self.publish_to_group(group_id, message_id)
        return message_id

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

    @staticmethod
    def set_message_id(post_id, message_id):
        body = {
            "id": post_id,
            "messageId": message_id
        }

        response = requests.put(f"{Endpoint.POST.value}", json=body)
        result = response.json().get("result")
        error = response.json().get("error")

        if response.status_code == 200:
            if result:
                logger.info(f"Post with id {post_id} has been set message id as {message_id}")
                return result

            elif error:
                logger.error(f"Update post message id request failed with error: {error}")

        else:
            logger.error(f"Update post message id request failed with status code: {response.status_code}, "
                         f"error: {error}")
