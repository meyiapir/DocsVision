from __future__ import annotations
import asyncio

from loguru import logger

from bot.core.config import settings
from bot.core.loader import bot, dp
from bot.handlers import get_handlers_router
from bot.middlewares import register_middlewares


async def startup() -> None:
    register_middlewares(dp)
    dp.include_router(get_handlers_router())

    bot_info = await bot.get_me()

    logger.info(f"Name     - {bot_info.full_name}")
    logger.info(f"Username - @{bot_info.username}")
    logger.info(f"ID       - {bot_info.id}")

    states: dict[bool | None, str] = {
        True: "Enabled",
        False: "Disabled",
        None: "Unknown (This's not a bot)",
    }

    logger.info(f"Groups Mode  - {states[bot_info.can_join_groups]}")
    logger.info(f"Privacy Mode - {states[not bot_info.can_read_all_group_messages]}")
    logger.info(f"Inline Mode  - {states[bot_info.supports_inline_queries]}")

    logger.info("bot started")


async def shutdown() -> None:
    logger.info("bot stopping...")

    await dp.storage.close()
    await dp.fsm.storage.close()

    logger.info("bot stopped")


async def main_polling() -> None:
    logger.debug("bot starting...")

    logger.add(
        "logs/bot_debug.log",
        level="DEBUG",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="100 KB",
        compression="zip",
    )

    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main_polling())
