from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import GpuNodeModel
from bot.external_api.utils.check_gpu import check_gpu
from bot.filters import text
from bot.filters.gpus import GpusFilter
from bot.keyboards.inline.gpus import gpu_actions_keyboard, gpu_check_delete, gpus_keyboard, main_gpus_keyboard, \
    node_type_keyboard
from bot.services.generations import GenerationsQueueService
from bot.services.nodes import (
    create_gpu_node,
    delete_gpu_node,
    get_all_gpu_nodes,
    get_gpu_node,
    get_user_gpus,
    pause_gpu_node,
    update_gpu_host,
)
from bot.services.users import get_user_info, is_admin
from bot.states import user
from bot.states.gpus import GpusStates
from bot.utils.locales import get_all_locales

router = Router(name="gpus")
DELETE_GPU = False


@router.message(text.TextFilter(get_all_locales("gpu menu")), GpusFilter())
@router.message(Command("gpus"), GpusFilter())
async def gpus(message: types.Message, state: FSMContext) -> None:
    if message.text in get_all_locales("gpu menu"):
        await message.delete()
    await message.answer("Привет, тут можешь выбрать действие с GPU", reply_markup=main_gpus_keyboard())
    await state.set_state(user.UserMainMenu.menu)


@router.callback_query(F.data.startswith("my_gpus"))
async def my_gpus(query: types.CallbackQuery, session: AsyncSession) -> None:
    user_is_admin = await is_admin(session=session, user_id=query.from_user.id)
    if user_is_admin:
        user_gpus = await get_all_gpu_nodes(session)
    else:
        user_gpus = await get_user_gpus(session, str(query.from_user.id))
    gpu_texts = {}
    for gpu in user_gpus:
        user_data = await get_user_info(session, gpu.tg_id, to_str=False)
        gpu_texts[gpu.id] = f"{gpu.name} [{user_data.first_name}]" if user_is_admin and int(
            gpu.tg_id) != query.from_user.id \
            else gpu.name
    await query.message.answer("Твои GPU", reply_markup=gpus_keyboard(gpus=gpu_texts))
    await session.close()


@router.callback_query(F.data.startswith("my_gpu_stats"))
async def my_gpu_stats(query: types.CallbackQuery, session: AsyncSession) -> None:
    user_is_admin = await is_admin(session=session, user_id=query.from_user.id)
    if user_is_admin:
        user_gpus = await get_all_gpu_nodes(session)
    else:
        user_gpus = await get_user_gpus(session, str(query.from_user.id))
    stats_text = ""
    for gpu in user_gpus:
        eta_speed = gpu.eta_seconds if gpu.eta_seconds > -1 else "~"
        queue_service = GenerationsQueueService(session)
        queue_count = await queue_service.count_queue_by_gpu_id(str(gpu.id))
        user_data = await get_user_info(session, gpu.tg_id, to_str=False)
        gpu_name = f"{gpu.name} [{user_data.first_name}]" if user_is_admin and int(gpu.tg_id) != query.from_user.id \
            else gpu.name

        stats_text += (f"GPU: {gpu_name}\nКоличество обработок: {gpu.processings_count}\nСкорость: {eta_speed} сек."
                       f"\nСтатус: {'Активен' if gpu.is_active else 'На паузе'}\nОчередь: {queue_count}\n\n")
    await query.message.answer(f"Статистика GPU:\n\n{stats_text}")
    await session.close()


@router.callback_query(F.data.startswith("my_gpu_add"))
async def my_gpu_add(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Выбери тип сервиса:", reply_markup=node_type_keyboard())
    await state.set_state(GpusStates.add_gpu_type)


@router.callback_query(F.data.startswith("add_gpu_type_"))
async def add_gpu_type(query: types.CallbackQuery, state: FSMContext) -> None:
    node_type = query.data.replace("add_gpu_type_", "")
    await state.update_data(node_type=node_type)

    if node_type == "ddcn":
        await query.message.answer("Отправь Ngrok адрес без https://\n\nПример: ea87-188-134-89-86.ngrok-free.app")
    else:
        await query.message.answer("Отправь адрес сервиса")


    await state.set_state(GpusStates.add_gpu_host)


@router.message(GpusStates.add_gpu_host)
async def add_gpu_host(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    node_type = data["node_type"]
    await message.answer("Теперь отправь название GPU") if node_type == "ddcn" else await message.answer("Теперь отправь название сервиса")

    await state.update_data(host=message.text)
    await state.set_state(GpusStates.add_gpu_name)


@router.message(GpusStates.add_gpu_name)
async def add_gpu_name(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Теперь отправь максимальное количество обработок в формате числа\n\nВведи '-1' для бесконечного количества")
    await state.update_data(name=message.text)
    await state.set_state(GpusStates.add_gpu_max_processings)


@router.message(GpusStates.add_gpu_max_processings)
async def add_gpu_processings(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    gpu_host = data["host"]
    gpu_name = data["name"]
    node_type = data["node_type"]
    try:
        gpu_max_pr = int(message.text)
    except ValueError:
        await message.answer("Неверное значение, необходимо ввести число")
        return
    if node_type == "ddcn":
        status_msg = await message.answer("Проверка доступности хоста...")
        gpu = GpuNodeModel(tg_id=str(message.from_user.id), host=gpu_host, name=gpu_name, processings_max=gpu_max_pr)
        check = await check_gpu(gpu, session)
    else:
        status_msg = await message.answer("Добавляю новый сервис!")
        check = [True, 0]
    if check[0]:
        new_gpu = await create_gpu_node(
            session=session,
            tg_id=str(message.from_user.id),
            host=gpu_host,
            name=gpu_name,
            max_processings=gpu_max_pr,
            eta_seconds=check[1],
            node_type=node_type
        )
        if new_gpu:
            await status_msg.edit_text(
                f"Готово, ты добавил сервис\n\nХост: {gpu_host}\nИмя: {gpu_name}\nМаксимум обработок: {gpu_max_pr}")
        else:
            await status_msg.edit_text("Что-то пошло не так, попробуй еще раз")
    else:
        await status_msg.edit_text("Хост недоступен")

    await state.set_state(user.UserMainMenu.menu)
    await session.close()


@router.callback_query(F.data.startswith("select_gpu_"))
async def select_gpu(query: types.CallbackQuery, session: AsyncSession) -> None:
    gpu_id = int(query.data.split("_")[-1])
    gpu = await get_gpu_node(session, gpu_id)
    await query.message.answer(f"Выбрано GPU: {gpu.name}\n\nХост: {gpu.host}\n"
                               f"Максимум обработок: {gpu.processings_max}\n"
                               f"ETA: {gpu.eta_seconds if gpu.eta_seconds > -1 else '~'} сек.\n"
                               f"Тип: {gpu.node_type}\n\n"
                               f"Статус: {'Активен' if gpu.is_active else 'На паузе'}",
                               reply_markup=gpu_actions_keyboard(gpu.id, gpu.is_active))
    await session.close()


@router.callback_query(F.data.startswith("gpu_pause_"))
async def gpu_pause(query: types.CallbackQuery, session: AsyncSession) -> None:
    gpu_id = int(query.data.split("_")[-1])
    gpu = await get_gpu_node(session, gpu_id)
    await pause_gpu_node(session, gpu_id, gpu.is_active)
    await query.message.edit_text(f"Выбрано GPU: {gpu.name}\n\nХост: {gpu.host}\n"
                                  f"Максимум обработок: {gpu.processings_max}\n"
                                  f"ETA: {gpu.eta_seconds if gpu.eta_seconds > -1 else '~'} сек.\n\n"
                                  f"Статус: {'Активен' if gpu.is_active else 'На паузе'}",
                                  reply_markup=gpu_actions_keyboard(gpu.id, gpu.is_active))
    await session.close()


@router.callback_query(F.data.startswith("gpu_edit_host_"))
async def gpu_edit_host(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Отправь новый хост")
    await state.set_state(GpusStates.edit_gpu_host)
    await state.update_data(gpu_id=int(query.data.split("_")[-1]))


@router.message(GpusStates.edit_gpu_host)
async def edit_gpu_host(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    gpu_id = data["gpu_id"]
    gpu = await get_gpu_node(session, gpu_id)
    if gpu.host == message.text:
        await message.answer("Новый хост совпадает со старым, ничего не изменилось")
        await state.set_state(user.UserMainMenu.menu)
        return
    msg_status = await message.answer("Проверка доступности хоста...")
    gpu.host = message.text
    check = await check_gpu(gpu, session)
    if check[0]:
        await update_gpu_host(session, gpu_id, message.text)
        await msg_status.edit_text("Хост изменен")
        await state.set_state(user.UserMainMenu.menu)
    else:
        await msg_status.edit_text("Хост недоступен")
    await session.close()


@router.callback_query(F.data.startswith("gpu_delete_check_"))
async def gpu_delete_check(query: types.CallbackQuery) -> None:
    await query.message.answer("Точно удалить?", reply_markup=gpu_check_delete(int(query.data.split("_")[-1])))


@router.callback_query(F.data.startswith("gpu_delete_"))
async def gpu_delete(query: types.CallbackQuery, session: AsyncSession) -> None:
    if DELETE_GPU:
        gpu_id = int(query.data.split("_")[-1])
        await delete_gpu_node(session, gpu_id)
        await query.message.delete()
        await query.message.answer("GPU удалено")
    else:
        await query.message.answer("Функция отключена, обратитесь к админу")
    await session.close()
