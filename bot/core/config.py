from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DIR = Path(__file__).absolute().parent.parent.parent
BOT_DIR = Path(__file__).absolute().parent.parent


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str
    RATE_LIMIT: int | float = 0.5


class MongoSettings(EnvBaseSettings):
    MONGODB_URL: str


class Settings(BotSettings, MongoSettings):
    API_HOST: str
    DOC_TYPES_DICT: dict[str, str] = {
        "proxy": "Доверенность",
        "contract": "Договор",
        "act": "Акт",
        "application": "Заявление",
        "order": "Приказ",
        "invoice": "Счёт",
        "bill": "Приложение",
        "arrangement": "Соглашение",
        "contractoffer": "Д-вор оферты",
        "statute": "Устав",
        "determination": "Решение"
    }


settings = Settings()
