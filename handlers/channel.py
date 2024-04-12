from aiogram import Bot, F, Router, types
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import settings, LANGS
from bot.keyboards.inline.channel import check_channel_sub_button
from bot.services.users import set_main_channel_sub, get_language_code
from bot.utils.check_channel import check_channel_sub

router = Router(name="channel")


@router.callback_query(F.data.startswith("check_channel_sub"))
async def check_channel_sub_handler(
        callback_query: types.CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    language_code = await get_language_code(session, callback_query.from_user.id)
    if language_code not in LANGS:
        language_code = 'en'

    chat_id = settings.CHANNEL_CHAT_IDS.get(language_code).get('id')
    user_id = callback_query.from_user.id

    user_sub = await check_channel_sub(bot=bot, chat_id=chat_id, user_id=user_id)
    await set_main_channel_sub(session=session, user_id=user_id, user_sub=user_sub)
    if user_sub:
        await bot.send_message(chat_id=user_id, text=_("subscribe channel check true"))
    else:
        await bot.send_message(chat_id=user_id, text=_("subscribe channel check false"),
                               reply_markup=check_channel_sub_button())
    await session.close()
