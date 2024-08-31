from enum import Enum
from config_reader import config


class PostStatus(Enum):
    AWAITS = "AWAITS"
    PUBLISHED = "PUBLISHED"
    ERROR = "ERROR"


class PublicationStatus(Enum):
    TEXT = "TEXT"
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"
    ANIMATION = "ANIMATION"


class Endpoint(Enum):
    BASE_URL = config.API_BASE_URL + "/api"
    GROUP = f"{BASE_URL}/group"
    POST = f"{BASE_URL}/post"

    def __str__(self):
        return self.value
