import os

from aiogram import Bot, Router, types
from aiogram.types import FSInputFile
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import BOT_DIR
from bot.filters import text
from bot.keyboards.inline.processings import to_processing_keyboard
from bot.services.quota import get_quota
from bot.services.users import get_language_code
from bot.utils.locales import get_all_locales
from bot.utils.profile_image import find_images_with_prefix, generate_profile_image, get_user_avatar

router = Router(name="profile")


@router.message(text.TextFilter(get_all_locales("profile keyboard")))
async def profile_handler(message: types.Message, session: AsyncSession, bot: Bot) -> None:
    if message.from_user is None:
        return
    await message.delete()

    user_lang = await get_language_code(session, message.from_user.id)
    if user_lang in ["ru", "uk"]:
        file = f"{BOT_DIR}/res/templates/profile/profile_{user_lang}.jpg"
    else:
        file = f"{BOT_DIR}/res/templates/profile/profile_en.jpg"
    avatar = await get_user_avatar(message, bot)
    user_quota = await get_quota(session, message.from_user.id)
    earned_quota = 0

    if os.path.exists(
            f"{BOT_DIR}/temp/customized_avatars/customized_{message.from_user.id}_avatar{user_quota}_{earned_quota}.png"
    ):
        profile_photo = (
            f"{BOT_DIR}/temp/customized_avatars/customized_{message.from_user.id}_avatar{user_quota}_{earned_quota}.png"
        )
    else:
        paths = await find_images_with_prefix(f"customized_{message.from_user.id}_avatar")
        for i in paths:
            os.remove(i)
        profile_photo = await generate_profile_image(
            file, avatar, message.from_user.id, message.from_user.first_name, user_quota
        )
    await bot.send_photo(
        message.from_user.id,
        FSInputFile(profile_photo),
        caption=_("profile message").format(first_name=message.from_user.first_name),
        reply_markup=to_processing_keyboard()
    )
    await session.close()
