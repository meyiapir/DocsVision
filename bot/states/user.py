from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    set_types = State()
    send_files = State()