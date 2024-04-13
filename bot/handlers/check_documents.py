import os
import io

from aiogram import Bot, Router, types, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputFile
from loguru import logger

from bot.core.config import settings
from bot.keyboards.inline.approve_end_file_send import approve_end_file_send_keyboard
from bot.keyboards.inline.approve_types import approve_types_keyboard
from bot.keyboards.inline.back_to_files import back_to_files_keyboard
from bot.keyboards.inline.end_file_send import end_file_send_keyboard
from bot.keyboards.inline.start import start_keyboard
from bot.keyboards.inline.type_params import type_params_keyboard
from bot.states.user import UserState

from bot.lib.rtf_parser import parse_rtf_header

router = Router(name="check_documents")


@router.callback_query(F.data.startswith('check_documents'))
async def set_types(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Welcome message."""
    await state.set_state(UserState.set_types.state)
    state_data = await state.get_data()

    doc_type_params = {item[0]: item[1] for item in state_data.items() if item[0] in settings.DOC_TYPES_DICT}
    if not doc_type_params:
        await state.update_data(
            {doc_type: 0 for doc_type in settings.DOC_TYPES_DICT}
        )

    await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                         caption=f'Выберите требуемые количества документов соответствующих типов:',
                         parse_mode=ParseMode.HTML, reply_markup=type_params_keyboard(**doc_type_params))


@router.callback_query(F.data.startswith('set_type_'))
async def value_change_handler(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
     doc_type, value = call.data.split('_')[2:4]

     await state.update_data(
         {doc_type: int(value)}
     )

     state_data = await state.get_data()
     doc_type_params = {item[0]: item[1] for item in state_data.items() if item[0] in settings.DOC_TYPES_DICT}

     await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                    caption=f'Выберите требуемые количества документов соответствующих типов:',
                                    parse_mode=ParseMode.HTML, reply_markup=type_params_keyboard(**doc_type_params))


@router.callback_query(F.data.startswith('set_types_finish'))
async def approve_types(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    state_data = await state.get_data()
    doc_type_params = {item[0]: item[1] for item in state_data.items() if item[0] in settings.DOC_TYPES_DICT if item[1]}

    if doc_type_params:
        docs_counts = [f"<b>{settings.DOC_TYPES_DICT[doc_type]}</b>: {value}" for doc_type, value in doc_type_params.items()]
        docs_counts = "\n".join(docs_counts)

        await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                       caption=f'Вот количества Ваших документов: \n{docs_counts}\n\nПродолжить?',
                                       parse_mode=ParseMode.HTML, reply_markup=approve_types_keyboard())

    else:
        await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                       caption=f'Вы не указали количества документов.',
                                       parse_mode=ParseMode.HTML, reply_markup=approve_types_keyboard(back=True))


@router.callback_query(F.data.startswith('approve_types'))
async def files_notif(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    await state.set_state(UserState.send_files.state)
    msg_id = await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                caption=f'Отправьте документы',
                                parse_mode=ParseMode.HTML,
                                reply_markup=end_file_send_keyboard())

    await state.update_data(docs=[])

    await state.update_data(doc_msg_id=msg_id.message_id)


@router.message(F.document, UserState.send_files)
async def get_documents(message: types.Message, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()
    docs = data.get('docs') or []

    docs.append(message.document.file_id)

    await bot.delete_message(message.from_user.id, data.get('doc_msg_id'))
    menu_image = FSInputFile(f'{os.path.curdir}/bot/files/static/main_menu.jpg')
    msg_id = await bot.send_photo(message.from_user.id, menu_image, caption='Отправьте документы',
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=end_file_send_keyboard())

    await state.update_data(doc_msg_id=msg_id.message_id, docs=docs)

@router.callback_query(F.data.startswith('end_file_send'))
async def approve_end_file_send(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()

    logger.debug(data)

    if data.get('docs'):
        await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                    caption="Файлы получены.",
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=approve_end_file_send_keyboard())
    else:
        await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                    caption="Вы не отправили ни одного файла",
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=back_to_files_keyboard()
                                    )


@router.callback_query(F.data.startswith('clear_documents'))
async def clear_documents(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    await state.update_data(docs=[])
    await call.answer('Список документов очищен')


@router.callback_query(F.data.startswith('calculate_files'))
async def calculate_files(call: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    await state.set_state(None)

    data = await state.get_data()

    file_ids = data.get('docs')

    response = {doc_type: 0 for doc_type in settings.DOC_TYPES_DICT}

    for file_id in file_ids:
        file = io.BytesIO()
        await bot.download(file_id, file)
        file.seek(0)
        parsed = parse_rtf_header(file.read().decode('utf-8'))
        r = 'proxy'
        response[r] += 1

    res_message = ''

    for doc_type in settings.DOC_TYPES_DICT:
        if response.get(doc_type):
            value = response[doc_type]
        else:
            value = 0

        if data.get(doc_type):
            required_value = data[doc_type]
        else:
            required_value = 0

        if value != data.get(doc_type):
            res_message += f"<b>{settings.DOC_TYPES_DICT[doc_type]}:</b> {value} шт., должно быть {required_value}\n"

    if res_message:
        await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                    caption=res_message,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=start_keyboard(retry=True))
    else:
        await bot.edit_message_caption(call.from_user.id, call.message.message_id,
                                       caption="Все документы в порядке!",
                                       parse_mode=ParseMode.HTML,
                                       reply_markup=start_keyboard())

        await state.update_data({'docs': []})
        await state.clear()
