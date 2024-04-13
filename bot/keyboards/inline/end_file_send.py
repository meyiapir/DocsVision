from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def end_file_send_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Я отправил все файлы", callback_data="end_file_send")],
        [InlineKeyboardButton(text="Очистить список документов", callback_data="clear_documents")]
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
