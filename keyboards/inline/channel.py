from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.config import settings


def channel_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Use when call support query."""
    channel = settings.CHANNEL_CHAT_IDS.get(language_code)
    if not channel:
        if 'en' in settings.CHANNEL_CHAT_IDS:
            channel = settings.CHANNEL_CHAT_IDS.get('en')
        else:
            return None

    buttons = [
        [InlineKeyboardButton(text=_("first subscribe to this channel button"), url=channel.get('url'))],
        [InlineKeyboardButton(text=_("subscribe channel check button"), callback_data="check_channel_sub")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()


def check_channel_sub_button() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=_("subscribe channel check false button"), callback_data="check_channel_sub")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
