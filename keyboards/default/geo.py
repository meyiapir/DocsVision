from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.i18n import gettext as _


def location_request_keyboard():
    button1 = KeyboardButton(text=_("send my geo button"), request_location=True)
    button2 = KeyboardButton(text=_("skip geo button"))
    return ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[[button1, button2]])
