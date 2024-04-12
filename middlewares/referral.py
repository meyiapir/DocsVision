from __future__ import annotations
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.utils.i18n import gettext as _
from loguru import logger

from bot.core.config import settings
from bot.services import quota, users
from bot.services.users import get_language_code
from bot.utils import misc
from bot.utils.command import find_command_argument
from bot.utils.locales import translate

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


class ReferralMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any]
    ) -> Any:
        message: Message = event

        if not message.from_user:
            return await handler(event, data)

        user_id = message.from_user.id
        session: AsyncSession = data["session"]
        bot = data["bot"]
        is_first_login = data["is_first_login"]

        referrer = find_command_argument(message.text)
        if referrer:
            user_data = await users.get_user_info(session, user_id, to_str=False)
            if not user_data.referrer and await users.user_exists(session, referrer) and referrer != user_id and is_first_login:
                await users.set_referrer(session, user_id, referrer)
                await quota.give_quota(session, user_id, settings.REFERRER_QUOTA_GIVE)
                await quota.give_quota(session, referrer, settings.REFERRER_QUOTA_EARN)

                referrer_lang_code = await get_language_code(session, referrer)

                await bot.send_message(referrer,
                    translate("user used invite", referrer_lang_code).format(
                        user_full_name=message.from_user.full_name,
                        referrer_quota=settings.REFERRER_QUOTA_EARN))
                await message.answer(_("invited by referrer").format(referrer_quota=settings.REFERRER_QUOTA_GIVE))
                await misc.log_referral(bot=bot, session=session, user_id=str(user_id), referral_id=referrer)
        return await handler(event, data)
