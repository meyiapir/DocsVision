from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def approve_types_keyboard(back=False) -> InlineKeyboardMarkup:
    """Use when call support query."""

    buttons = [
        [InlineKeyboardButton(text="Продолжить ➡️", callback_data="approve_types")],
        [InlineKeyboardButton(text="Вернуться назад ⬅️", callback_data="check_documents")],
    ]

    if back:
        buttons = buttons[1:]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
