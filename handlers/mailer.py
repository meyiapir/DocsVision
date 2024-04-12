from datetime import datetime as dt
from datetime import timedelta

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters import text
from bot.keyboards.inline.mailer import mailer_keyboard
from bot.services.mailings import MailingService
from bot.services.users import is_admin, get_user_info
from bot.states import mailer, user
from bot.utils.locales import get_all_locales
from bot.utils.sender import send_to_users, extract_text_schema

router = Router(name="mailer")


@router.message(
    text.TextFilter(get_all_locales("start mailing")),
)
async def request_mailing(message: types.Message, session: AsyncSession, state: FSMContext) -> None:
    if await is_admin(session, message.from_user.id):
        await state.clear()
        await state.set_state(mailer.Mailer.set_time)
        await message.delete()
        await message.answer(_("set time"))
    await session.close()


@router.message(
    mailer.Mailer.set_time
)
async def set_time(message: types.Message, state: FSMContext) -> None:
    try:
        if message.text:
            dt_obj = dt.strptime(message.text.strip(), "%d.%m.%y %H:%M")
            if dt_obj > (dt.now() + timedelta(hours=3)):
                await state.update_data(dt_obj=dt_obj.strftime("%d.%m.%y %H:%M"))
                await state.set_state(mailer.Mailer.set_message)
                await message.answer(_("mailing message request"))
            else:
                await message.answer(_("past time error"))
                await message.answer(_("set time"))
        else:
            await message.answer(_("wrong time format"))
            await message.answer(_("set time"))

    except ValueError:
        await message.answer(_("wrong time format"))
        await message.answer(_("set time"))


@router.message(
    F.photo | F.video | F.audio | F.document,
    mailer.Mailer.set_message
)
async def add_media(message: types.Message, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()

    media = data.get("media") or []
    media_types = {x["type"] for x in media}
    mix_audio_err = False
    max_attachments_err = False

    if len(media) < 10:
        if message.audio:
            if media_types and "audio" not in media_types:
                mix_audio_err = True
            else:
                media.append(
                    {
                        "file_id": message.audio.file_id,
                        "type": "audio"
                    })
                await message.answer(_("audio added"))
        else:
            if "audio" in media_types:
                mix_audio_err = True

            else:
                if message.photo:
                    media.append(
                        {
                            "file_id": message.photo[-1].file_id,
                            "type": "photo"
                        })
                    await message.answer(_("photo added"))

                if message.video:
                    media.append(
                        {
                            "file_id": message.video.file_id,
                            "type": "video"
                        })
                    await message.answer(_("video added"))

                if message.document:
                    media.append(
                        {
                            "file_id": message.document.file_id,
                            "type": "document"
                        })
                    await message.answer(_("document added"))

        if mix_audio_err:
            await message.answer(_("unable to mix audio"))

    else:
        max_attachments_err = True
        await message.answer(_("max 10 attachments"))

    text = message.text if message.text else message.caption

    if text:
        schema = extract_text_schema(text)
        if schema:
            await state.update_data(text=schema)
            await message.answer(_("text updated"))
        else:
            await message.answer(_("schema creation error"))
            schema = data.get('text') or {}
    else:
        schema = data.get("text") or {}

    if not any((max_attachments_err, mix_audio_err)):
        await state.update_data(media=media)

    user = await get_user_info(session, message.from_user.id, to_str=False)

    await send_to_users(bot, session, schema, media, users=[user])
    await message.answer(_("choose action"), reply_markup=mailer_keyboard())
    await session.close()


@router.message(
    F.text,
    mailer.Mailer.set_message
)
async def set_message(message: types.Message, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()

    media = data.get("media") or []
    text = message.text if message.text else message.caption

    schema = extract_text_schema(text)

    if schema:
        await state.update_data(text=schema)
        await message.answer(_("text updated"))

        user = await get_user_info(session, message.from_user.id, to_str=False)

        await send_to_users(bot, session, schema, media, users=[user])
        await message.answer(_("choose action"), reply_markup=mailer_keyboard())

    else:
        await message.answer(_("schema creation error"))
    await session.close()


@router.callback_query(
    F.data == "clear_media",
    mailer.Mailer.set_message
)
async def clear_media(callback_query: types.CallbackQuery, session: AsyncSession, state: FSMContext, bot: Bot) -> None:
    await callback_query.message.delete()

    await state.update_data(media=[])

    data = await state.get_data()
    text = data.get("text") or {}

    schema = extract_text_schema(text)

    user = await get_user_info(session, callback_query.from_user.id, to_str=False)

    await bot.send_message(callback_query.from_user.id, _("media cleared"))
    await send_to_users(bot, session, schema, [], users=[user])
    await bot.send_message(callback_query.from_user.id, _("choose action"), reply_markup=mailer_keyboard())
    await session.close()


@router.callback_query(
    F.data == "continue_mailing",
    mailer.Mailer.set_message
)
async def continue_mailing(callback_query: types.CallbackQuery, session: AsyncSession, state: FSMContext,
                           bot: Bot) -> None:
    data = await state.get_data()

    service = MailingService(session)

    if any((data.get('text'), data.get('media'))):
        await service.create_mailing(
            creator_id=str(callback_query.from_user.id),
            text=data.get("text") or {},
            media=data.get("media") or [],
            time=dt.strptime(data.get("dt_obj"), "%d.%m.%y %H:%M")
        )

        await callback_query.message.delete()
        await state.clear()
        await bot.send_message(callback_query.from_user.id, _("mailing added"))

        await state.set_state(user.UserMainMenu.menu)

    else:
        await bot.send_message(callback_query.from_user.id, _("empty mailing creation error"))
        await bot.send_message(callback_query.from_user.id, _("mailing message request"))
    await session.close()
