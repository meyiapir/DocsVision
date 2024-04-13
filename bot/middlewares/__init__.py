from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    from .throttling import ThrottlingMiddleware

    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())
