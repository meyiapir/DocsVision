from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def back_to_files_keyboard() -> InlineKeyboardMarkup:
    """Use when call support query."""

    buttons = [
        [InlineKeyboardButton(text="Вернуться назад ⬅️", callback_data="approve_types")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
