from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.utils.i18n import gettext as _
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import settings
from bot.filters.admin import AdminFilter
from bot.services.db_backup import create_backup
from bot.services.generations import GenerationsQueueService
from bot.services.quota import get_quota, give_quota, take_quota
from bot.services.user_analytics import delete_user_analytics
from bot.services.users import (
    get_first_name,
    get_user_geo,
    get_user_info,
    is_block,
    set_is_block,
    set_is_noder,
    user_exists, delete_user,
)

router = Router(name="admin")


@router.message(Command("help_admin"), AdminFilter())
async def help_admin(message: types.Message) -> None:
    text = "Admin commands:\n\n" \
           "/chat_id - Get chat id\n" \
           "/topic - Get topic id\n" \
           "/get_user {user_id} - Get user info\n" \
           "/get_geo {user_id} - Get user location\n" \
           "/noder {user_id} - Set user as noder\n" \
           "/unnoder {user_id} - Remove user from noder\n" \
           "/bot_stats - Get bot stats"
    await message.answer(text)


@router.message(Command("chat_id"))
async def chat_id_handler(message: types.Message) -> None:
    await message.answer(f"chat_id {message.chat.id}")


@router.message(Command("topic"))
async def get_topic_id(message: types.Message) -> None:
    await message.answer(f"message_thread_id {message.message_thread_id}")


@router.message(Command("get_user"), AdminFilter())
async def get_user(message: types.Message, session: AsyncSession) -> None:
    get_tg_id = message.text.split(" ")
    if len(get_tg_id) > 1:
        get_tg_id = get_tg_id[1]
        if get_tg_id:
            get_user_data = await get_user_info(session, int(get_tg_id))
            await message.answer(f"get_user {get_user_data}")
            return
    await message.answer("Please provide a user id")
    await session.close()


@router.message(Command("get_geo"), AdminFilter())
async def get_geo(message: types.Message, session: AsyncSession, bot: Bot) -> None:
    get_tg_id = message.text.split(" ")
    if len(get_tg_id) > 1:
        get_tg_id = get_tg_id[1]
        if get_tg_id:
            get_user_data = await get_user_geo(session, int(get_tg_id))
            if get_user_data[0] is None or get_user_data[1] is None:
                await message.answer("User has not provided a location")
                return
            await bot.send_location(message.from_user.id, get_user_data[0], get_user_data[1])
            return
    await message.answer("Please provide a user id")
    await session.close()


@router.message(Command("noder"), AdminFilter())
async def give_status_noder(message: types.Message, session: AsyncSession) -> None:
    get_tg_id = message.text.split(" ")
    if len(get_tg_id) > 1:
        get_tg_id = get_tg_id[1]
        if get_tg_id:
            await set_is_noder(session, int(get_tg_id), True)
            await message.answer(f"User {get_tg_id} is now a noder")
            return
    await message.answer("Please provide a user id")
    await session.close()


@router.message(Command("unnoder"), AdminFilter())
async def remove_status_noder(message: types.Message, session: AsyncSession) -> None:
    get_tg_id = message.text.split(" ")
    if len(get_tg_id) > 1:
        get_tg_id = get_tg_id[1]
        if get_tg_id:
            await set_is_noder(session, int(get_tg_id), False)
            await message.answer(f"User {get_tg_id} is no longer a noder")
            return
    await message.answer("Please provide a user id")
    await session.close()


@router.message(Command("bot_stats"), AdminFilter())
async def bot_stats(message: types.Message, session: AsyncSession) -> None:
    queue_service = GenerationsQueueService(session)
    get_queue = await queue_service.count_generations_in_queue()
    text = f"Queue tasks: {get_queue}"
    await message.answer(f"Bot stats:\n\n{text}")
    await session.close()


@router.message(Command("block"), AdminFilter())
async def block_user(message: types.Message, session: AsyncSession, bot: Bot) -> None:
    args = message.text.split()[1:]

    if args:
        user_id = int(args[0])
        if await user_exists(session, user_id):
            get_user_data = await is_block(session, user_id)
            if get_user_data:
                await message.answer("User is already blocked")
                return

            if len(args) == 2:
                msg_id = f"ban message {args[1].strip()}"
                if _(msg_id) != msg_id:
                    await bot.send_message(user_id, _(msg_id))
                else:
                    await message.answer("Irregular message keyword")
                    return

            await set_is_block(session, user_id, True)
            await message.answer(f"User {await get_first_name(session, user_id)} successfully blocked")
            return
        else:
            await message.answer("User does not exist")
            return

    await message.answer("Use: /block {tg_id} {msg} (e.g. child)")
    await session.close()


@router.message(Command("unblock"), AdminFilter())
async def unblock_user(message: types.Message, session: AsyncSession, bot: Bot) -> None:
    get_tg_id = message.text.split(" ")
    if len(get_tg_id) > 1:
        user_id = int(get_tg_id[1])
        if await user_exists(session, user_id):
            get_user_data = await is_block(session, user_id)
            if not get_user_data:
                await message.answer("User is already unblocked")
                return

            await set_is_block(session, user_id, False)
            await bot.send_message(user_id, _("unban message"))
            await message.answer(f"User {await get_first_name(session, user_id)} successfully unblocked")
            return
        else:
            await message.answer("User does not exist")
            return

    await message.answer("Please provide a user id")
    await session.close()


@router.message(Command("set_quota"), AdminFilter())
async def set_quota(message: types.Message, session: AsyncSession) -> None:
    get_tg_id = message.text.split(" ")
    if len(get_tg_id) > 2:
        user_id = int(get_tg_id[1])
        if await user_exists(session, user_id):
            if get_tg_id[2][0] == "-" and get_tg_id[2][1:].isdigit():
                first = await get_quota(session, user_id)
                if await take_quota(session, message.from_user.id, int(get_tg_id[2][1:])):
                    second = await get_quota(session, user_id)
                    await message.answer(
                        f"{await get_first_name(session, user_id)} user quota successfully decreased: {first} -> {second}")
                    return
                await message.answer("Too much for this user")
            elif get_tg_id[2].isdigit():
                first = await get_quota(session, user_id)
                await give_quota(session, message.from_user.id, int(get_tg_id[2]))
                second = await get_quota(session, user_id)
                await message.answer(
                    f"{await get_first_name(session, user_id)} user quota successfully increased: {first} -> {second}")

            return
    await message.answer("Please provide a user id")
    await session.close()


@router.message(Command("delete_me"), AdminFilter())
async def delete_me(message: types.Message, session: AsyncSession) -> None:
    try:
        chat_id = message.from_user.id
        if await user_exists(session=session, user_id=chat_id):
            await delete_user_analytics(session=session, user_id=chat_id)
            await delete_user(session=session, user_id=chat_id)
            await message.answer("You are now deleted")
        else:
            await message.answer("User does not exist")
    except Exception as e:
        await message.answer("Error deleting user")
        logger.error(str(e))
    await session.close()


@router.message(Command("backup"), AdminFilter())
async def create_db_backup(message: types.Message, bot: Bot) -> None:
    file_path, file_name = create_backup()
    if file_path and file_name:
        in_file = FSInputFile(file_path)
        logger.debug(in_file)
        await bot.send_document(chat_id=settings.LOG_GROUP_ID, document=in_file,
                                message_thread_id=13490, caption=file_name, disable_notification=True)
        await message.answer(text="Done!")
    else:
        await bot.send_message(chat_id=settings.LOG_GROUP_ID, message_thread_id=13490, text="Error :(")
