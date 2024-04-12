from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.core.config import settings


def gen_params_keyboard(style, **kwargs) -> InlineKeyboardMarkup:
    if not settings.GENERATION_PARAMS_CONFIG[style]:
        buttons = [[InlineKeyboardButton(text=_("continue"), callback_data='gen_params_finish')]]
        keyboard = InlineKeyboardBuilder(markup=buttons)

        return keyboard.as_markup()

    gen_config = settings.GENERATION_PARAMS_CONFIG[style]

    buttons = []

    for param in gen_config:
        buttons.append([])

        if kwargs.get(param):
            param_value = kwargs.get(param)
        else:
            param_value = gen_config[param]["values"][gen_config[param]["default"]]

        callback_data = f'gen_param_next_{param}_{param_value}'

        buttons[-1].append(InlineKeyboardButton(text=_(f'gen param {param.replace("_", " ")}'),
                                                callback_data=callback_data))

        if kwargs.get(param):
            buttons[-1].append(InlineKeyboardButton(text=_(f'gen param {param.replace("_", " ")} {param_value}'),
                                 callback_data=callback_data))
        else:
            buttons[-1].append(InlineKeyboardButton(text=_(f'gen param {param.replace("_", " ")} {param_value}'),
                                 callback_data=callback_data))

    buttons.append([InlineKeyboardButton(text=_("continue"), callback_data='gen_params_finish')])

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
