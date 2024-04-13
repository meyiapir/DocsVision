from aiogram import Router


def get_handlers_router() -> Router:
    from . import (
        null,
        start,
        check_documents
    )

    router = Router()
    router.include_router(null.router)
    router.include_router(start.router)
    router.include_router(check_documents.router)

    return router
