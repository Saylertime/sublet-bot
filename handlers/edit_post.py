from pg_maker import (
    find_my_sublets,
    change_post,
    type_of_sublet,
    delete_post,
    status_of_sublet,
    update_photos,
    get_active_sublets,
)
from utils import show_post
from keyboards import create_markup
from states.overall import OverallState
import asyncio
from datetime import datetime


from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ContentType
from aiogram_calendar import DialogCalendar


router_edit = Router()


@router_edit.message(Command("edit_post"))
@router_edit.callback_query(F.data == "edit_post")
async def edit_post(message, state):
    await state.clear()
    try:
        buttons = await find_my_sublets(str(message.from_user.id))

        if buttons:
            buttons = [(address, str(user_id)) for address, user_id in buttons]
            buttons.append(("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"))
            markup = create_markup(buttons)
            if isinstance(message, CallbackQuery):
                await message.message.edit_text(
                    "Какое объявление нужно отредактировать?", reply_markup=markup
                )
            else:
                await message.answer(
                    "Какое объявление нужно отредактировать?", reply_markup=markup
                )
        else:
            buttons = [
                ("Создать объявление", "add_post"),
                ("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"),
            ]
            markup = create_markup(buttons)
            msg = "У вас пока нет объявлений"
            if isinstance(message, CallbackQuery):
                await message.message.edit_text(msg, reply_markup=markup)
            else:
                await message.answer(msg, reply_markup=markup)
    except Exception as e:
        print(e)


@router_edit.message(OverallState.edit)
@router_edit.callback_query(F.data == "Назад")
async def choose_edit_button(message, state):
    post_id = (await state.get_data()).get("post_id", "")
    is_active = await status_of_sublet(post_id)

    buttons = [
        (f"⏻ {'Отключить пост' if is_active else 'Активировать пост'} ⏻",
         f"{'is_active_False' if is_active else 'is_active_True'}"),
        ("🛌 Изменить тип саблета 🛌", "Изменить тип саблета"),
        ("📬 Изменить адрес 📬", "Изменить адрес"),
        ("📝 Изменить описание 📝", "Изменить описание"),
        ("📸 Изменить фотографии 📸", "Изменить фотографии"),
        ("📅 Изменить даты 📅", "Изменить даты"),
        ("📰 Посмотреть пост 📰", "Посмотреть пост"),
        ("🗑️ Удалить пост 🗑️", "Удалить пост"),
        ("⬇ Назад к моим объявлениям ⬇", "edit_post"),
        ("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"),
    ]
    markup = create_markup(buttons)

    if isinstance(message, CallbackQuery):
        await message.message.edit_text("Что хотите изменить?", reply_markup=markup)
    else:
        await message.answer("Что хотите изменить?", reply_markup=markup)


@router_edit.callback_query(F.data == "Изменить тип саблета")
@router_edit.message(OverallState.change_type)
async def change_type(message, state):
    all_types = ["Квартира", "Комната"]
    post_id = (await state.get_data()).get("post_id", "")
    my_type = await type_of_sublet(post_id)
    all_types.remove(my_type)

    markup = create_markup(
        [
            (f"Изменить на {all_types[0]}", f"Изменить на {all_types[0]}"),
            ("⬇ Назад ⬇", "Назад"),
        ]
    )
    await message.message.edit_text(f"Сейчас выбран тип {my_type}", reply_markup=markup)


@router_edit.callback_query(F.data.startswith("Изменить на"))
async def change_type_final(message, state):
    post_id = (await state.get_data()).get("post_id", "")
    await change_post(
        post_id=post_id, parameter_name="type", parameter=message.data.split()[2]
    )
    await message.answer("Тип изменён!")
    await choose_edit_button(message, state)


@router_edit.callback_query(F.data.startswith("is_active_"))
async def disable_ad(message, state):
    flag = message.data.split("_")[2]
    is_active = flag == "True"
    post_id = (await state.get_data()).get("post_id", "")
    await change_post(post_id=post_id, parameter_name="is_active", parameter=is_active)
    await choose_edit_button(message, state)


@router_edit.callback_query(F.data == "Изменить адрес")
async def change_address(message, state):
    await message.message.edit_text("Напишите новый адрес")
    await state.set_state(OverallState.edit_address)


@router_edit.message(OverallState.edit_address)
async def edit_address(message, state):
    await state.update_data(new_adress=message.text)
    post_id = (await state.get_data()).get("post_id", "")
    await change_post(post_id=post_id, parameter_name="address", parameter=message.text)
    await message.answer("Адрес изменен!")
    await choose_edit_button(message, state)


@router_edit.callback_query(F.data == "Изменить описание")
async def change_description(message, state):
    await message.message.edit_text("Введите новое описание")
    await state.set_state(OverallState.edit_description)


@router_edit.message(OverallState.edit_description)
async def edit_description(message, state):
    await state.update_data(new_description=message.text)
    post_id = (await state.get_data()).get("post_id", "")
    await change_post(
        post_id=post_id, parameter_name="description", parameter=message.text
    )
    await message.answer("Описание изменено!")
    await choose_edit_button(message, state)


@router_edit.callback_query(F.data == "Изменить фотографии")
async def change_photos(message, state):
    await message.message.edit_text(
        "Залейте новые фото вместо старых (все сразу, максимум 8 штук)"
    )
    await state.set_state(OverallState.change_photos)
    await state.update_data(photos=[])
    await handle_album_photo(message.message, state)


media_groups = {}
timers = {}
MAX_PHOTOS = 8


@router_edit.message(
    F.media_group_id, F.content_type == ContentType.PHOTO, OverallState.change_photos
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

    post_id = (await state.get_data()).get("post_id", "")

    if group_id in media_groups:
        album = media_groups.pop(group_id)
        timers.pop(group_id, None)

        await state.update_data(photos=album)
        await update_photos(int(post_id), album)
        await message.answer(f"{len(album) if len(album) <=8 else 8} фото загружены!")
        await choose_edit_button(message, state)


@router_edit.callback_query(F.data == "Посмотреть пост")
async def see_post(message, state):
    post_id = (await state.get_data()).get("post_id", "")
    result = await get_active_sublets(post_id=int(post_id), flag="my_post")
    await show_post(message, result)

    buttons = [
        ("➕ Создать новое объявление ➕", "add_post"),
        ("⬇ Вернуться к этому объявлению ⬇", "Назад"),
        ("⬇⬇ Посмотреть все мои объявления ⬇⬇", "edit_post"),
        ("⬇⬇⬇ Вернуться в меню ⬇⬇⬇", "start"),
    ]
    markup = create_markup(buttons)
    await message.message.answer("Что дальше?", reply_markup=markup)


@router_edit.callback_query(F.data == "Удалить пост")
async def delete_post_from_db(message, state):
    post_id = (await state.get_data()).get("post_id", "")
    await delete_post(int(post_id))
    await message.message.edit_text("Объявление удалено!")
    await edit_post(message, state)


@router_edit.callback_query(F.data == "Изменить даты")
async def change_check_in(message, state):
    await state.update_data(stage="change_check_in")
    await message.message.edit_text(
        "Выберите дату заезда",
        reply_markup=await DialogCalendar().start_calendar(
            year=datetime.now().year, month=datetime.now().month
        ),
    )


@router_edit.message(OverallState.change_dates)
async def change_check_out(message, state):
    await state.update_data(stage="change_check_out")
    await message.answer(
        "Выберите дату выезда",
        reply_markup=await DialogCalendar().start_calendar(
            year=datetime.now().year, month=datetime.now().month
        ),
    )


@router_edit.callback_query(F.data.regexp(r"^\d+$"))
async def edit_post_callback(message, state):
    post_id = message.data
    await state.update_data(post_id=post_id)
    await state.set_state(OverallState.edit)
    await choose_edit_button(message, state)


@router_edit.message(
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
    OverallState.change_photos,
)
async def not_photo_group(message):
    await message.answer("Нужно отправить фотографии альбомом. Попробуйте ещё раз")
