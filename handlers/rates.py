from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.rates import like_dislike

router = Router(name="rates")


@router.callback_query(F.data.startswith("like"))
async def like(query: types.CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    await like_dislike(rate=True, query=query, session=session, bot=bot,
                       state=state)


@router.callback_query(F.data.startswith("dislike"))
async def dislike(query: types.CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    await like_dislike(rate=False, query=query, session=session, bot=bot,
                       state=state)
