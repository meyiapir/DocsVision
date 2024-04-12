from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import settings
from bot.filters import text
from bot.filters.location import LocationFilter
from bot.keyboards.default import basic
from bot.keyboards.default.geo import location_request_keyboard
from bot.services.quota import give_quota
from bot.services.user_analytics import get_coins_from_tasks, set_coins_from_tasks
from bot.services.users import save_user_geo
from bot.utils.locales import get_all_locales
from bot.states import geo

router = Router(name="get_geo")


@router.message(text.TextFilter(get_all_locales("skip geo button")))
async def skip_location_handler(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    await save_user_geo(session, message.from_user.id, 0, 0)
    await state.clear()

    await message.answer(_("skip geo message"), reply_markup=basic.StartButtons.start())
    await session.close()


@router.message(
    LocationFilter(),
    geo.GeoStates.get_geo
)
async def location_handler(message: types.Message, state: FSMContext,  session: AsyncSession, bot: Bot) -> None:
    """Обработка полученной геопозиции."""
    if message.location:
        # Получение геопозиции пользователя
        latitude = message.location.latitude
        longitude = message.location.longitude

        await save_user_geo(session, message.from_user.id, latitude, longitude)
        await give_quota(session, message.from_user.id, 2)

        coins_from_tasks = await get_coins_from_tasks(session, message.from_user.id)

        await set_coins_from_tasks(session, message.from_user.id, coins_from_tasks + 2)
        await message.answer(_("geo success"), reply_markup=basic.StartButtons.start())

        log_msg = await bot.send_location(
            settings.LOG_GROUP_ID, latitude, longitude, disable_notification=True, message_thread_id=151
        )
        await bot.send_message(
            settings.LOG_GROUP_ID,
            f"User <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>\n\nLatitude: {latitude}\nLongitude: {longitude}",
            reply_to_message_id=log_msg.message_id,
            disable_web_page_preview=True
        )

        await state.clear()

    else:
        # Если геопозиция по каким-то причинам не была получена
        await message.answer(_("geo get error"), reply_markup=location_request_keyboard())
    await session.close()
