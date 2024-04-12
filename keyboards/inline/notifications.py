from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def notification_keyboard() -> InlineKeyboardMarkup:
    """Use in main menu."""
    buttons = [
        [InlineKeyboardButton(text=_("clear media"), callback_data="clear_media")],
        [InlineKeyboardButton(text=_("continue"), callback_data="add_notification")]
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()