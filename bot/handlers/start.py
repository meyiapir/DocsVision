from aiogram import Bot, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import settings
from bot.keyboards.default import basic
from bot.services import users
from bot.states import user

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(
        message: types.Message,
        session: AsyncSession,
        bot: Bot,
        state: FSMContext,
) -> None:
    """Welcome message."""
    from_user = message.from_user

    user_data = await users.get_user_info(session, from_user.id, to_str=False)

    user_quota = user_data.quota
    user_is_noder = user_data.is_noder
    user_is_admin = user_data.is_admin
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={from_user.id}"
    welcome_message = _("first message").format(full_name=from_user.full_name, user_quota=user_quota,
                                                get_referral_coins=settings.REFERRER_QUOTA_EARN,
                                                referral_link=referral_link)

    await message.delete()
    await message.answer(welcome_message, disable_web_page_preview=True,
                         reply_markup=basic.StartButtons.start(is_noder=user_is_noder,
                                                               is_admin=user_is_admin))

    await state.set_state(user.UserMainMenu.menu)
    await session.close()
