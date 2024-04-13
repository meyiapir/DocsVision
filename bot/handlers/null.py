from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext

router = Router(name="null")


@router.callback_query(F.data.startswith('null'))
async def null(call: types.Message, state: FSMContext) -> None:
    pass