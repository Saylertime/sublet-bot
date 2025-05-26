from handlers.add_post import final
from keyboards import create_markup
from pg_maker import update_photos
from states.overall import OverallState
import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import ContentType


router_photos = Router()

media_groups = {}
timers = {}
MAX_PHOTOS = 8


@router_photos.message(F.media_group_id, F.content_type == ContentType.PHOTO)
async def handle_photos(message, state):
    current_state = await state.get_state()

    if (
        current_state == OverallState.photos.state
        or current_state == OverallState.change_photos.state
    ):
        await handle_album_photo(message, state)


async def handle_album_photo(message, state):
    if not getattr(message, "media_group_id", None) or not message.photo:
        return

    group_id = message.media_group_id

    if group_id not in media_groups:
        media_groups[group_id] = []

    if message.photo:
        media_groups[group_id].append(message.photo[-1].file_id)

    if group_id in timers:
        timers[group_id].cancel()

    timers[group_id] = asyncio.create_task(
        finalize_album(group_id, message.chat.id, state, message)
    )


async def finalize_album(group_id, chat_id, state, message):
    await asyncio.sleep(2)

    post_id = (await state.get_data()).get("post_id", "")

    if group_id in media_groups:
        album = media_groups.pop(group_id)
        timers.pop(group_id, None)

        await state.update_data(photos=album)
        await message.answer(f"{len(album) if len(album) <=8 else 8} фото загружены!")
        current_state = await state.get_state()

        if current_state == OverallState.change_photos:
            await state.update_data(photos=album)
            await update_photos(int(post_id), album)
            buttons = [
                ("➕ Создать новое объявление ➕", "add_post"),
                ("⬇ Вернуться к этому объявлению ⬇", "Назад"),
                ("⬇⬇ Посмотреть все мои объявления ⬇⬇", "edit_post"),
                ("⬇⬇⬇ Вернуться в меню ⬇⬇⬇", "start"),
            ]
            markup = create_markup(buttons)
            await message.answer("Что дальше?", reply_markup=markup)

        elif current_state == OverallState.photos:
            await final(message, state)


@router_photos.message(
    F.content_type.in_(
        {
            ContentType.PHOTO,
            ContentType.TEXT,
            ContentType.DOCUMENT,
            ContentType.VIDEO,
            ContentType.AUDIO,
            ContentType.VOICE,
            ContentType.STICKER,
        }
    ),
    StateFilter(OverallState.change_photos, OverallState.photos),
)
async def not_photo_group(message, state):
    current_state = await state.get_state()
    if (
        current_state == OverallState.photos.state
        or current_state == OverallState.change_photos.state
    ):
        await message.reply(
            "Нужно отправить фотографии альбомом (минимум 2 штуки и максимум 8. Попробуйте ещё раз"
        )
