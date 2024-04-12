from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.processings import ProcessingService


async def processing_keyboard(session: AsyncSession) -> InlineKeyboardMarkup:
    """Use in main menu."""
    processing_service = ProcessingService(session)

    processings = await processing_service.get_all_processings()

    buttons = [
        [InlineKeyboardButton(text=_(processing.pack_msg_id), callback_data=f'processing_{processing.id}'),
         InlineKeyboardButton(text=f'{processing.price} RUB', callback_data=f'processing_{processing.id}'),
         ] for processing in processings
    ]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()


def to_processing_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=_('buy processings'), callback_data='processings_menu')]]

    keyboard = InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()