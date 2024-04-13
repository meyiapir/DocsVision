from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.middlewares.album import AlbumMiddleware


def register_middlewares(dp: Dispatcher) -> None:
    from .logging import LoggingMiddleware
    from .throttling import ThrottlingMiddleware

    dp.message.outer_middleware(ThrottlingMiddleware())

    dp.update.outer_middleware(LoggingMiddleware())

    dp.callback_query.middleware(CallbackAnswerMiddleware())

    dp.message.middleware(AlbumMiddleware())