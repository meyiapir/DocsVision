from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_gpus_keyboard() -> InlineKeyboardMarkup:
    buttons = [

        [InlineKeyboardButton(text="Мои GPU", callback_data="my_gpus")],
        [InlineKeyboardButton(text="Статистика", callback_data="my_gpu_stats")],
        [InlineKeyboardButton(text="Добавить", callback_data="my_gpu_add")]

    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()


def gpus_keyboard(gpus: dict) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=gpus[gpu], callback_data=f"select_gpu_{gpu}")
        ]
        for gpu in gpus
    ] if gpus else [[InlineKeyboardButton(text="Добавить", callback_data="my_gpu_add")]]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()


def gpu_actions_keyboard(gpu_id: int, pause_state: bool) -> InlineKeyboardMarkup:
    buttons_pause_off = [
        [InlineKeyboardButton(text="На паузу", callback_data=f"gpu_pause_{gpu_id}")],
        [InlineKeyboardButton(text="Изменить хост", callback_data=f"gpu_edit_host_{gpu_id}")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"gpu_delete_check_{gpu_id}")]
    ]
    buttons_pause_on = [
        [InlineKeyboardButton(text="Возобновить", callback_data=f"gpu_pause_{gpu_id}")],
        [InlineKeyboardButton(text="Изменить хост", callback_data=f"gpu_edit_host_{gpu_id}")],
        [InlineKeyboardButton(text="Удалить", callback_data=f"gpu_delete_check_{gpu_id}")]
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons_pause_off if pause_state else buttons_pause_on)

    return keyboard.as_markup()


def gpu_check_delete(gpu_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Да", callback_data=f"gpu_delete_{gpu_id}")],
        [InlineKeyboardButton(text="Нет", callback_data="my_gpus")]
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()

def node_type_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Cloud Provider", callback_data="add_gpu_type_cloud")],
        [InlineKeyboardButton(text="DDCN Node", callback_data="add_gpu_type_ddcn")],
        [InlineKeyboardButton(text="MAPI Node", callback_data="add_gpu_type_mapi")],
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
