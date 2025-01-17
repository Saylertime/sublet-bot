from states.overall import OverallState
from pg_maker import new_post, get_active_sublets
from handlers.free import show_variants
from utils import show_post
import asyncio
from datetime import datetime
from keyboards import all_cities, create_markup
from config_data import config

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ContentType
from aiogram_calendar import DialogCalendar

router_add_post = Router()


@router_add_post.message(Command("add_post"))
@router_add_post.callback_query(F.data == "add_post")
async def add_post(message, state):
    await state.set_state(OverallState.add_post)
    name = message.from_user.username
    if isinstance(message, CallbackQuery):
        message = message.message

    if not name:
        await message.answer(
            "Пожалуйста, введите свой контакт или номер телефона. "
            "Эта информация будет указана в объявлении"
        )
    else:
        await start_post(message, state)


@router_add_post.message(OverallState.add_post)
async def start_post(message, state):
    try:
        await state.update_data(command="add_post")
        if message.from_user.username is None:
            await state.update_data(contact=message.text)
        await all_cities(message)
    except Exception as e:
        print(str(e))


@router_add_post.callback_query(F.data.in_(tuple(config.CITIES)))
async def city_callback(message, state):
    try:
        await state.update_data(city=message.data)
        command = (await state.get_data()).get("command", "")
        if command == "add_post":
            await state.set_state(OverallState.type)
            await type_of_sublet(message.message, state)

        elif command == "free":
            await state.set_state(OverallState.free_show)
            await show_variants(message, state)
    except Exception as e:
        print(str(e))


@router_add_post.message(OverallState.type)
async def type_of_sublet(message, state):
    buttons = [
        (
            "Квартира",
            "Тип Квартира",
        ),
        ("Комната", "Тип Комната"),
    ]
    markup = create_markup(buttons)
    await message.edit_text("Выберите тип саблета: ", reply_markup=markup)


@router_add_post.callback_query(F.data.startswith("Тип"))
async def type_of_sublet_callback(message, state):
    await state.update_data(type=message.data.split()[1])
    await state.set_state(OverallState.address)
    await address(message, state)


@router_add_post.message(OverallState.address)
async def address(message, state):
    await state.set_state(OverallState.description)
    await message.message.edit_text("Напишите адрес: ")


@router_add_post.message(OverallState.description)
async def description(message, state):
    await state.update_data(address=message.text)
    await message.answer(
        "Опишите саблет. Здесь можно оставить свои контакты и добавить эмодзи 🏠\n\n"
        "ВНИМАНИЕ: максимальная длина сообщения — 700 символов"
    )
    await state.set_state(OverallState.check_in)


@router_add_post.message(OverallState.check_in)
async def check_in(message, state):
    if len(message.text) < 700:
        await state.update_data(description=message.text, stage="check_in")
        await message.answer(
            "Выберите дату заезда",
            reply_markup=await DialogCalendar().start_calendar(
                year=datetime.now().year, month=datetime.now().month
            ),
        )
    else:
        await message.answer(
            "Описание слишком длинное. Сократите его до 700 знаков и попробуйте еще раз"
        )


@router_add_post.message(OverallState.check_out)
async def check_out(message, state, stage):
    await state.update_data(stage=stage)
    await message.answer(
        "Выберите дату выезда",
        reply_markup=await DialogCalendar().start_calendar(
            year=datetime.now().year, month=datetime.now().month
        ),
    )


media_groups = {}
timers = {}
MAX_PHOTOS = 8


@router_add_post.message(
    F.media_group_id, F.content_type == ContentType.PHOTO, OverallState.photos
)
async def handle_album_photo(message, state):
    group_id = message.media_group_id

    if group_id not in media_groups:
        media_groups[group_id] = []

    media_groups[group_id].append(message.photo[-1].file_id)

    if group_id in timers:
        timers[group_id].cancel()

    timers[group_id] = asyncio.create_task(
        finalize_album(group_id, message.chat.id, state, message)
    )


async def finalize_album(group_id, chat_id, state, message):
    await asyncio.sleep(2)

    if group_id in media_groups:
        album = media_groups.pop(group_id)
        timers.pop(group_id, None)

        await state.update_data(photos=album)
        await message.answer(f"{len(album)} загружены!")
        await final(message, state)


async def final(message, state):
    data = await state.get_data()
    contact = message.from_user.username or data["contact"]
    check_in_date = datetime.strptime(data["check_in"], "%Y-%m-%d")
    check_out_date = datetime.strptime(data["check_out"], "%Y-%m-%d")
    try:
        await new_post(
            username=contact,
            user_id=str(message.from_user.id),
            city=data["city"],
            address=data["address"],
            type=data["type"],
            description=data["description"],
            date_in=check_in_date,
            date_out=check_out_date,
            photos=data.get("photos", []),
        )

        result = await get_active_sublets(flag="last_post")
        await show_post(message, result, is_admin=True)
        buttons = [
            ("Посмотреть или отредактировать мои объявления", "edit_post"),
            ("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"),
        ]
        markup = create_markup(buttons)
        await message.answer("Пост опубликован!!", reply_markup=markup)
    except Exception as e:
        await message.answer(str(e))


@router_add_post.message(
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
    F.state.in_([OverallState.photos, OverallState.change_photos]),
)
async def not_photo_group(message):
    await message.answer("Нужно отправить фотографии альбомом. Попробуйте ещё раз")
