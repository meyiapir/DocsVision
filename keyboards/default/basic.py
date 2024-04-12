import aiogram.types
from aiogram.utils.i18n import gettext as _

from .consts import DefaultConstructor


class StartButtons(DefaultConstructor):
    @staticmethod
    def start(is_noder=False, is_admin=False) -> aiogram.types.ReplyKeyboardMarkup:
        add_args_count = int(is_noder) + int(is_admin)

        match add_args_count:
            case 0:
                schema = [1, 2]
            case 1:
                schema = [1, 2, 2] if is_admin else [1, 2, 1]
            case 2:
                schema = [1, 2, 1, 2]

        btns = [("processings keyboard"), _("profile keyboard")]
        if is_noder:
            btns.append(_("gpu menu"))
        if is_admin:
            btns.append(_("start mailing"))
            btns.append(_("start notification"))

        return StartButtons._create_kb(btns, schema)


class BasicButtons(DefaultConstructor):
    @staticmethod
    def back() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["◀️Назад"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def cancel() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def back_n_cancel() -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1, 1]
        btns = ["◀️Назад", "🚫 Отмена"]
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def confirmation(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.ReplyKeyboardMarkup:
        schema = []
        btns = []
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        schema.append(1)
        btns.append("✅Подтвердить")
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def skip(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["▶️Пропустить"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["✅Да"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def no(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [1]
        btns = ["❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)

    @staticmethod
    def yes_n_no(add_back: bool = False, add_cancel: bool = False) -> aiogram.types.ReplyKeyboardMarkup:
        schema = [2]
        btns = ["✅Да", "❌Нет"]
        if add_back:
            schema.append(1)
            btns.append("◀️Назад")
        if add_cancel:
            schema.append(1)
            btns.append("🚫 Отмена")
        return BasicButtons._create_kb(btns, schema)
