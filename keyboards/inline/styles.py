from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def styles_keyboard() -> InlineKeyboardMarkup:
    """Use in main menu."""
    buttons = [
        [
            InlineKeyboardButton(text=_("male style"), callback_data="style_male"),
            InlineKeyboardButton(text=_("female style"), callback_data="style_female"),
        ],
        [InlineKeyboardButton(text=_("lingerie style"), callback_data="style_lingerie")],
        [InlineKeyboardButton(text=_("bdsm style"), callback_data="style_bdsm")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
