from datetime import datetime

from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.users import set_is_left

router = Router(name="bot_ban")


@router.my_chat_member()
async def ban_bot(my_chat_member: types.ChatMemberUpdated, session: AsyncSession) -> None:
    new_status = my_chat_member.new_chat_member.status
    if new_status == "kicked":
        await set_is_left(session, my_chat_member.from_user.id, datetime.now())
    elif new_status != "kicked":
        await set_is_left(session, my_chat_member.from_user.id, None)
    await session.close()
