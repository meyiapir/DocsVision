from aiogram import Router


def get_handlers_router() -> Router:
    from . import (
        admin,
        channel,
        export_users,
        get_geo,
        gpus,
        language,
        mailer,
        mask_generate,
        notifications,
        processings,
        profile,
        rates,
        start,
        support,
        get_anal,
        bot_ban
    )

    router = Router()
    router.include_router(start.router)
    router.include_router(language.router)
    router.include_router(support.router)
    router.include_router(export_users.router)
    router.include_router(mailer.router)
    router.include_router(notifications.router)
    router.include_router(mask_generate.router)
    router.include_router(processings.router)
    router.include_router(profile.router)
    router.include_router(get_geo.router)
    router.include_router(admin.router)
    router.include_router(get_anal.router)
    router.include_router(gpus.router)
    router.include_router(rates.router)
    router.include_router(channel.router)
    router.include_router(bot_ban.router)

    return router
