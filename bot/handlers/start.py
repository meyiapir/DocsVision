import os.path

from aiogram import Bot, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from bot.keyboards.inline.start import start_keyboard

router = Router(name="start")

@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    menu_image = FSInputFile(f'{os.path.curdir}/bot/files/static/main_menu.jpg')

    await message.answer_photo(menu_image, caption=f'Добро пожаловать, <b>{message.from_user.full_name}!</b>',
                         parse_mode=ParseMode.HTML, reply_markup=start_keyboard())

    await state.clear()
