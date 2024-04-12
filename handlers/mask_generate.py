import base64
import io
from datetime import datetime, timedelta

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.utils.i18n import gettext as _
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core.config import settings
from bot.filters import media, text
from bot.keyboards.default.geo import location_request_keyboard
from bot.keyboards.inline.gen_params import gen_params_keyboard
from bot.keyboards.inline.styles import styles_keyboard
from bot.services.generations import GenerationsQueueService
from bot.services.quota import take_quota
from bot.services.users import get_user_geo, is_admin
from bot.states import geo, user
from bot.streamline.client import StreamLineClient
from bot.utils import misc
from bot.utils.heartbeats import BetterUptime
from bot.utils.locales import get_all_locales

router = Router(name="mask_generate")


@router.message(text.TextFilter())
@router.message(Command("generate"))
async def generate_setup(msg: types.Message, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    if msg.from_user is None:
        return

    await msg.delete()
    user_geo = await get_user_geo(session=session, user_id=msg.from_user.id)
    if user_geo[0] is None or user_geo[1] is None:
        await state.set_state(geo.GeoStates.get_geo)
        await msg.answer(_("geo please"), reply_markup=location_request_keyboard())
        return

    await misc.send_instruction(bot, msg.from_user.id)
    await bot.send_photo(msg.from_user.id, f"{settings.FS_HOST}/cchYFLm8BPVhN;ER/image/back1.png",
                         caption=_("generate-setup"))


@router.message(
    media.ImageFilter(),
)
async def generate_start(msg: types.Message, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    if msg.from_user is None:
        return

    if msg.photo:
        user_is_admin = await is_admin(session, msg.from_user.id)
        if user_is_admin:
            quota = True
        else:
            quota = await take_quota(session, msg.from_user.id, 1)

        if quota:
            photo = msg.photo[-1]

            style_msg = await bot.send_message(msg.from_user.id, _("choose style"), reply_markup=styles_keyboard())
            await state.update_data({f'_g{str(style_msg.message_id)}_{datetime.now().strftime("%Y_%m_%d_%H_%M")}':
                                         (photo.file_id,
                                          user_is_admin)})

        else:
            await msg.answer(_("coins not enough"))
    else:
        await msg.answer(_("image processing error 2"))

    data = await state.get_data()
    if len(data.keys()) > 100:
        await state.clear()


async def log_image(is_bro: bool, bot: Bot, photo_file_id: str, gen_mask: FSInputFile, gen_file: FSInputFile,
                    log_message: str) -> int:
    try:
        if settings.LOG_GROUP_ID:
            if not is_bro:
                msg = await bot.send_media_group(
                    chat_id=settings.LOG_GROUP_ID,
                    media=[InputMediaPhoto(media=photo_file_id),
                           InputMediaPhoto(media=gen_mask),
                           InputMediaPhoto(media=gen_file,
                                           caption=log_message)],
                    disable_notification=True,
                    message_thread_id=132,
                )
                logger.debug("EVERYTHING IS OKAY")
                return msg[1].message_id
            else:
                msg = await bot.send_message(
                    chat_id=settings.LOG_GROUP_ID,
                    text=log_message,
                    disable_notification=True,
                    message_thread_id=132,
                )
                return msg.message_id
        else:
            logger.warning("LOG_GROUP_ID not set in .env file")
            return 0
    except Exception as e:
        logger.warning(f"Failed to log image: {e}")
        return 0


@router.callback_query(F.data.startswith("style_"))
async def generation_params(query: types.CallbackQuery, bot: Bot, state: FSMContext) -> None:
    await query.message.delete()

    style = query.data.replace("style_", "")
    await state.update_data(gen_style=style)

    style_config = settings.GENERATION_PARAMS_CONFIG[style]

    for param in style_config:
        await state.update_data({
            f"gen_param_{param}": style_config[param]["values"][style_config[param]["default"]]
        })

    data = await state.get_data()
    keys = [key for key in data if key.startswith(f"_g{query.message.message_id}")]
    val = data[keys[0]]

    settings_msg = await bot.send_message(query.from_user.id, _("gen params setting"),
                                          reply_markup=gen_params_keyboard(style))

    data.pop(keys[0])
    data.update({f'_g{str(settings_msg.message_id)}_{datetime.now().strftime("%Y_%m_%d_%H_%M")}': val})
    await state.update_data(data)


@router.callback_query(F.data.startswith("gen_param_next_"))
async def next_param(query: types.CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    data = await state.get_data()

    style = data.get("gen_style")
    params_data = query.data.replace("gen_param_next_", "")
    param, param_value = "_".join(params_data.split("_")[:-1]), params_data.split("_")[-1]

    param_config = settings.GENERATION_PARAMS_CONFIG[style][param]

    if param_value != param_config["values"][-1]:
        param_value = param_config["values"][param_config["values"].index(param_value) + 1]
    else:
        param_value = param_config["values"][0]

    await state.update_data({
        f"gen_param_{param}": param_value
    })

    data = await state.get_data()
    kwargs = {key.replace("gen_param_", ""): data[key] for key in data if "gen_param_" in key}

    await bot.edit_message_reply_markup(query.from_user.id, query.message.message_id,
                                        reply_markup=gen_params_keyboard(style, **kwargs))


@router.callback_query(F.data.startswith("gen_params_finish"))
async def generate_photo(query: types.CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext) -> None:
    if settings.USE_WEBHOOK:
        await BetterUptime().send_image_proc_start()
    data = await state.get_data()
    style = data.get("gen_style")

    gen_params = {key.replace("gen_param_", ""): value for key, value in data.items() if "gen_param_" in key}

    keys_to_remove = []
    current_time = datetime.now()
    for key in [i for i in list(data.keys()) if i[0] == "_"]:
        date = datetime.strptime(key[-16:], "%Y_%m_%d_%H_%M")
        if current_time - date > timedelta(hours=1):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del data[key]
    await state.clear()
    await state.update_data(data=data)

    queue_generation, status_msg, current_gpu = None, None, None

    try:
        keys = [key for key in data if key.startswith(f"_g{query.message.message_id}")]
        info = data[keys[0]]
        del data[keys[0]]
        await state.clear()
        await state.update_data(data=data)

        photo_file_id = info[0]
        user_is_admin = info[1]

        tg_id = query.from_user.id

        queue_service = GenerationsQueueService(session)
        user_queue_tasks = await queue_service.get_amount_queue_by_tg_id(str(tg_id))
        logger.info(f"User_Queue_Tasks: {user_queue_tasks}")

        try:
            if not user_is_admin and user_queue_tasks >= settings.USER_MAX_QUEUE_TASKS:
                await bot.send_message(tg_id, _("queue over").format(user_max_queue=settings.USER_MAX_QUEUE_TASKS))
                return

            await bot.edit_message_reply_markup(chat_id=tg_id,
                                                message_id=query.message.message_id)
            status_msg = await bot.edit_message_text(text=_("image processing").format(time="..."),
                                                     chat_id=tg_id,
                                                     message_id=query.message.message_id)

            photo_file = io.BytesIO()
            await bot.download(photo_file_id, photo_file)
            photo_file.seek(0)
            encoded_image = base64.b64encode(photo_file.read()).decode("utf-8")

            generation = await queue_service.create_generation(
                tg_id=str(tg_id),
                style=style,
                status="LV1_QUEUE",
                status_message=status_msg.message_id,
                bot_init_id=str(bot.id)
            )

            streamline_client = StreamLineClient(address=settings.RMQ_ADDRESS, outcoming_routing_key="ddcn_sl_lv1")

            gen_params.update({"style": style})

            send_to_queue = await streamline_client.publish({"image": encoded_image, "task_id": generation.id,
                                                             "gen_params": gen_params})
            logger.debug(send_to_queue)

        except Exception as e:
            logger.error(str(e))
            if status_msg:
                await status_msg.edit_text(_("image processing error"))
            else:
                await bot.send_message(tg_id, _("image processing error"))
            if queue_generation:
                await queue_service.finish_generation(generation_id=queue_generation.id,
                                                      gpu_id=str(current_gpu.id),
                                                      status="ERROR",
                                                      error_message=str(e))

    except Exception as e:
        logger.error(str(e))

        await bot.edit_message_reply_markup(chat_id=query.from_user.id,
                                            message_id=query.message.message_id)
        await bot.edit_message_text(text=_("expired"),
                                    chat_id=query.from_user.id,
                                    message_id=query.message.message_id)

        await state.set_state(user.UserMainMenu.menu)
