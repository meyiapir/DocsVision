from __future__ import annotations


from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger

from bot.core.config import LANGS
from bot.utils.locales import translate
from aiogram import Bot

users_commands = {
    lang: {
    "start": translate("main menu", lang),
    "lang": translate("change language", lang),
    "support": translate("support button", lang)
    } for lang in LANGS}


async def set_default_commands(bot: Bot) -> None:
    for language_code in users_commands:
        if language_code == "en":
            kwargs = dict(scope=BotCommandScopeDefault())
        else:
            kwargs = dict(scope=BotCommandScopeDefault(), language_code=language_code)

        await bot.delete_my_commands(**kwargs)

        await bot.set_my_commands(
            commands=[
                BotCommand(command=command, description=description)
                for command, description in users_commands[language_code].items()
            ],
            **kwargs
        )

        commands = await bot.get_my_commands(scope=BotCommandScopeDefault(), language_code=language_code)
        logger.info(commands)
