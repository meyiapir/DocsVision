from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def approve_end_file_send_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Далее ➡️", callback_data="calculate_files")],
        [InlineKeyboardButton(text="Вернуться назад ⬅️", callback_data="approve_types")]
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
