from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.config import settings


def type_params_keyboard(**kwargs) -> InlineKeyboardMarkup:
    buttons = []

    for doc_type in settings.DOC_TYPES_DICT:
        buttons.append([])

        if kwargs.get(doc_type):
            param_value = kwargs.get(doc_type)
        else:
            param_value = 0

        buttons[-1].append(InlineKeyboardButton(text=f'{settings.DOC_TYPES_DICT.get(doc_type)}: {param_value}',
                                                callback_data='null'))

        arrows = []

        if param_value > 0:
            arrows.append(InlineKeyboardButton(text="<<",
                                               callback_data=f"set_type_{doc_type}_{param_value - 1}"))
        else:
            arrows.append(InlineKeyboardButton(text="<<",
                                               callback_data="null"))

        arrows.append(InlineKeyboardButton(text=">>",
                                               callback_data=f"set_type_{doc_type}_{param_value + 1}"))

        buttons[-1].extend(arrows)

    buttons.append([InlineKeyboardButton(text="Продолжить ✔️", callback_data='set_types_finish')])

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
