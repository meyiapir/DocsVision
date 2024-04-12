from __future__ import annotations
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from loguru import logger

from bot.core.config import settings
from bot.services.user_analytics import add_user_analytics
from bot.services.users import add_user, is_block, user_exists

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.heartbeats import BetterUptime


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        session: AsyncSession = data["session"]
        message: Message = event
        user = message.from_user
        bot = data["bot"]

        if settings.USE_WEBHOOK:
            await BetterUptime().send_bot_use()

        if not user:
            return await handler(event, data)

        if await user_exists(session, user.id):
            data["is_first_login"] = False
            if not await is_block(session, user.id):
                return await handler(event, data)
            else:
                pass
                return None
        data["is_first_login"] = True

        logger.info(f"New User Registration | user_id: {user.id} | message: {message.text}")

        await add_user(session=session, user=user)
        await add_user_analytics(session=session, user=user)
        try:
            await bot.send_message(
                settings.LOG_GROUP_ID,
                f"👤 New user: <a href='tg://user?id={user.id}'>{user.full_name}</a>\nLink: tg://user?id={user.id}",
                disable_web_page_preview=False,
                message_thread_id=147,
            )
        except Exception as e:
            logger.error(str(e))

        return await handler(event, data)
