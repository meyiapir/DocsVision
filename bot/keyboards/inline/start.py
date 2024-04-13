from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.config import settings


def start_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Проверить документы 🔎", callback_data="check_documents")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
