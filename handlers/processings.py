from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters import text
from bot.keyboards.inline.processings import processing_keyboard
from bot.keyboards.inline.payments import payments_keyboard
from bot.utils.locales import get_all_locales

router = Router(name="processings")


@router.message(text.TextFilter(get_all_locales("processings keyboard")))
async def processings_handler(message: types.Message, session: AsyncSession) -> None:
    await message.delete()
    processing_kb = await processing_keyboard(session)
    await message.answer(_("processings"))
    #await message.answer(_("processings"), reply_markup=processing_kb)
    await session.close()


@router.callback_query(F.data.startswith('processings_menu'))
async def processings_callback_handler(callback_query: types.CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    processing_kb = await processing_keyboard(session)
    await bot.send_message(callback_query.from_user.id, _("processings"), reply_markup=processing_kb)
    await session.close()


@router.callback_query(F.data.startswith('processing_'))
async def processing_pack_handler(callback_query: types.CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    processing_id = int(callback_query.data.split("_")[-1])
    await callback_query.message.delete()
    await state.update_data(processing_id=processing_id)

    await bot.send_message(callback_query.from_user.id, _("choose paymethod"), reply_markup=payments_keyboard())
    await session.close()
