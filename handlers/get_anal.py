from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InputMediaPhoto
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin import AdminFilter
from bot.services.generations import GenerationsAnalyticsService
from bot.services.user_analytics import get_last_gen
from bot.services.users import get_created_at_users, get_geo_users, get_is_left_users, get_langs_users
from bot.utils.anal_tables import (
    analyze_distribution,
    avg_gen_day,
    avg_gen_per_hour,
    count_active_users,
    draw_geo_map,
    draw_pie,
    get_left_users_by_day,
    get_new_users_by_day,
    new_users_trend,
)

router = Router(name="get_anal")


@router.message(Command("anal"), AdminFilter())
async def get_analytics(message: types.Message, session: AsyncSession) -> None:
    await message.delete()
    status_msg = await message.answer("🔃 Сбор данных из БД...")

    try:
        gen_analytics_service = GenerationsAnalyticsService(session)

        all_created_at_all = await gen_analytics_service.get_generations_data(need_created_at=True)
        all_styles = await gen_analytics_service.get_styles_data()
        all_gens = await gen_analytics_service.get_generations_data(need_created_at=True, need_tg_id=True)
        users_created_at = await get_created_at_users(session)
        last_get_time = await get_last_gen(session)
        user_langs = await get_langs_users(session)
        get_geo = await get_geo_users(session)
        get_left = await get_is_left_users(session)

        image_avg_gen_per_hour = avg_gen_per_hour(all_created_at_all)
        image_avg_gen_per_day, median_events_per_day = avg_gen_day(all_created_at_all)

        users_trend = new_users_trend(users_created_at)
        left_trend = get_left_users_by_day(get_left)
        count_today = count_active_users(last_get_time)
        new_users_by_day = get_new_users_by_day(users_created_at)
        count_gens = analyze_distribution(data=all_gens)

        image_user_langs = draw_pie(data=user_langs, title="Пропорции использования языков", filename="lang_codes")
        image_user_styles = draw_pie(data=all_styles, title="Пропорции использования стилей", filename="styles")

        geo_map_html = draw_geo_map(data=get_geo)

        answer = await message.answer_media_group(
            media=[InputMediaPhoto(media=FSInputFile(image_avg_gen_per_hour)),
                   InputMediaPhoto(media=FSInputFile(image_avg_gen_per_day)),
                   InputMediaPhoto(media=FSInputFile(new_users_by_day)),
                   InputMediaPhoto(media=FSInputFile(left_trend)),
                   InputMediaPhoto(media=FSInputFile(image_user_langs)),
                   InputMediaPhoto(media=FSInputFile(image_user_styles)),
                   InputMediaPhoto(media=FSInputFile(count_gens)),
                   InputMediaPhoto(media=FSInputFile(users_trend),
                                   caption=f"Медианное кол-во генераций в день: {median_events_per_day}\n"
                                           f"Количество активных юзеров за сегодня: {count_today}")
                   ]
        )
        await message.answer_document(FSInputFile(geo_map_html), reply_to_message_id=answer[0].message_id)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"Ошибка получения аналитики: {e}")
        logger.error(str(e))
    await session.close()
