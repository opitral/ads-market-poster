from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    API_BASE_URL: str
    BOT_TOKEN: SecretStr
    ADMIN_TELEGRAM_IDS: Set[int]
    GENERAL_CHANNEL_TELEGRAM_ID: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
