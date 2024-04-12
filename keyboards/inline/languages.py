from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.utils.locales import get_flag_emoji
from bot.core.config import LANGS


def languages_keyboard() -> InlineKeyboardMarkup:
    """Use in main menu."""
    buttons = []

    for language_code in LANGS:
        language_code = 'ua' if language_code == 'uk' else language_code
        buttons.append(InlineKeyboardButton(text=f"{get_flag_emoji(language_code)} {language_code.upper()}", callback_data=f"set_lang_{language_code}"))

    kb_buttons = [buttons[i*3:i*3+3] for i in range((len(buttons)-1)//3+1)]

    keyboard = InlineKeyboardBuilder(markup=kb_buttons)

    return keyboard.as_markup()


languages_kb = languages_keyboard()
