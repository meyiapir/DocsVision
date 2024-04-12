from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DIR = Path(__file__).absolute().parent.parent.parent
BOT_DIR = Path(__file__).absolute().parent.parent

class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

class BotSettings(EnvBaseSettings):
    pass

class Settings(BotSettings):
    pass

settings = Settings()
