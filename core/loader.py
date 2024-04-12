from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage

from core.config import settings

token = settings.BOT_TOKEN

# if settings.PROXY:
#     logger.info("Using proxy")
#     bot = Bot(token=token, parse_mode=ParseMode.HTML, session=AiohttpSession(settings.PROXY))
# else:
#     bot = Bot(token=token, parse_mode=ParseMode.HTML)
bot = Bot(token=token, parse_mode=ParseMode.HTML)

storage = RedisStorage(
    redis=redis_client,
    key_builder=DefaultKeyBuilder(with_bot_id=True),
)

dp = Dispatcher(storage=storage)
