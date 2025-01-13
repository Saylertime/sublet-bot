from handlers.add_post import add_post
from pg_maker import (
    find_my_sublets,
    change_post,
    type_of_sublet,
    delete_post,
    status_of_sublet,
    update_photos,
    get_user_info_and_photos
)
from keyboards.reply.create_markup import create_markup
from states.overall import OverallState
import asyncio


from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ContentType, InputMediaPhoto


router_edit = Router()


@router_edit.message(Command("edit_post"))
@router_edit.callback_query(F.data == "edit_post")
async def edit_post(message, state):
    await state.clear()
    buttons = await find_my_sublets(str(message.from_user.id))

    if buttons:
        buttons = [(address, str(id)) for address, id in buttons]
        buttons.append(("⬇⬇⬇ Назад в меню ⬇⬇⬇", "Назад в меню"))
        markup = create_markup(buttons)
        if isinstance(message, CallbackQuery):
            await message.message.edit_text("Какое объявление нужно отредактировать?", reply_markup=markup)
        else:
            await message.answer("Какое объявление нужно отредактировать?", reply_markup=markup)
    else:
        buttons = ([('Создать объявление', 'Создать объявление'),
                    ('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')])
        markup = create_markup(buttons)
        await message.answer("У вас пока нет объявлений", reply_markup=markup)


@router_edit.message(OverallState.edit)
async def choose_edit_button(message):
    buttons = [('Аквтивировать/Отключить пост', 'Изменить статус'),
               ('Изменить тип саблета', 'Изменить тип саблета'),
               ('Изменить адрес', 'Изменить адрес'),
               ('Изменить описание', 'Изменить описание'),
               ('Изменить фотографии', 'Изменить фотографии'),
               ('Изменить даты', 'Изменить даты'),
               ('Посмотреть пост', 'Изменить посмотреть пост'),
               ('Удалить пост', 'Изменить удалить'),
               ('⬇ Назад к моим объявлениям ⬇', 'Посмотреть объявления'),
               ('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
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

    try:

        my_type = await type_of_sublet(post_id)
        print(my_type)
        all_types.remove(my_type)

        markup = create_markup([(f"Изменить на {all_types[0]}", f"Изменить на {all_types[0]}"),
                                ("⬇ Назад ⬇", "Назад")])
        await message.message.edit_text(f"Сейчас выбран тип {my_type}", reply_markup=markup)
    except Exception as e:
        print(str(e))
        await message.answer(str(e))


@router_edit.message(OverallState.change_status)
async def change_status(message, state):
    post_id = (await state.get_data()).get("post_id", "")
    my_type = await status_of_sublet(post_id)[0]
    if my_type:
        buttons = [("Отключить объявление", "Изменить на отключено объявление"),
                   ("Назад", "Назад")]
    else:
        buttons = [("Активировать объявление", "Изменить на  активировано"),
                   ("Назад", "Назад")]
    markup = create_markup(buttons)
    await message.message.edit_text(f'Сейчас объявление {"Активировано" if my_type else "Отключено"}',
                                    reply_markup=markup)


async def change_address(message, state):
    await message.message.edit_text("Напишите новый адрес")
    await state.set_state(OverallState.edit_address)


@router_edit.message(OverallState.edit_address)
async def edit_address(message, state):
    await state.update_data(new_adress=message.data)
    post_id = (await state.get_data()).get("post_id", "")
    await change_post(post_id=post_id, parameter_name="address", parameter=message.data)
    await message.answer("Адрес изменен!")
    await choose_edit_button(message)


async def change_description(message, state):
    await message.edit_text("Введите новое описание")
    await state.set_state(OverallState.edit_description)


@router_edit.message(OverallState.edit_description)
async def edit_description(message, state):
    await state.update_data(new_description=message.data)
    post_id = (await state.get_data()).get("post_id", "")
    await change_post(post_id=post_id, parameter_name='description', parameter=message.data)
    await message.answer("Описание изменено!")
    await choose_edit_button(message)


async def change_photos(message, state):
    await message.edit_text("Залейте новые фото вместо старых (все сразу, максимум 8 штук)")
    await state.set_state(OverallState.change_photos)
    await state.update_data(photos=[])


media_groups = {}
timers = {}
MAX_PHOTOS = 8


@router_edit.message(F.media_group_id, F.content_type == ContentType.PHOTO, OverallState.change_photos)
async def handle_album_photo(message, state):
    group_id = message.media_group_id

    if group_id not in media_groups:
        media_groups[group_id] = []

    media_groups[group_id].append(message.photo[-1].file_id)

    if group_id in timers:
        timers[group_id].cancel()

    timers[group_id] = asyncio.create_task(finalize_album(group_id, message.chat.id, state, message))


async def finalize_album(group_id, chat_id, state, message):
    await asyncio.sleep(2)

    if group_id in media_groups:
        album = media_groups.pop(group_id)
        timers.pop(group_id, None)

        await state.update_data(photos=album)
        await message.answer(f"{len(album)} загружены!")
        await choose_edit_button(message)


async def see_post(message, state):
    post_id = (await state.get_data()).get("post_id", "")
    result = await get_user_info_and_photos(post_id)
    media = [
        InputMediaPhoto(media=file_id, caption=result[0][0])
        if idx == 0 else InputMediaPhoto(media=file_id)
        for idx, file_id in enumerate(result[0][1])
    ]
    await message.answer_media_group(media)

    buttons = [('Создать новое объявление', 'Создать объявление'),
               ('⬇ Посмотреть все мои объявления ⬇', 'Посмотреть объявления'),
               ('⬇⬇ Вернуться к этому объявлению ⬇⬇', 'Назад'),
               ('⬇⬇⬇ Вернуться в меню ⬇⬇⬇', 'Назад в меню')]
    markup = create_markup(buttons)
    await message.answer(message.from_user.id, "Что дальше?", reply_markup=markup)


@router_edit.callback_query(F.data.regexp(r"^\d+$"))
async def edit_post_callback(message, state):
    post_id = message.data
    await state.update_data(post_id=post_id)
    await state.set_state(OverallState.edit)
    await choose_edit_button(message)


# #КНОПКИ С ИЗМЕНЕНИЯМИ
# @bot.callback_query_handler(func=lambda call: call.data.startswith('Изменить'))
# def choose_buttons_callback(call):
#     with bot.retrieve_data(call.from_user.id) as data:
#         post_id = data['post_id']
#     if call.data == 'Изменить тип саблета':
#         change_type(call)
#     elif call.data == 'Изменить адрес':
#         change_address(call)
#     elif call.data == 'Изменить описание':
#         change_description(call)
#     elif call.data == 'Изменить посмотреть пост':
#         see_post(call)
#     elif call.data == 'Изменить статус':
#         change_status(call)
#     elif call.data == 'Изменить фотографии':
#         change_photos(call)
#     elif call.data == 'Изменить удалить':
#         try:
#             delete_post(post_id)
#             edit_post(call)
#         except:
#             bot.send_message(call.from_user.id, 'Что-то пошло не так. Возможно, пост уже удален?')
#     elif call.data == 'Изменить даты':
#         with bot.retrieve_data(call.from_user.id) as data:
#             data['command'] = 'edit_post'
#         show_calendar(bot, call.from_user.id)
#
#     elif 'Изменить на' in call.data:
#         if call.data == 'Изменить на отключено объявление':
#             change_post(post_id=post_id, parameter_name='is_active', parameter=False)
#         elif call.data == 'Изменить на  активировано':
#             change_post(post_id=post_id, parameter_name='is_active', parameter=True)
#         else:
#             change_post(post_id=post_id, parameter_name='type', parameter=call.data.split()[2])
#         choose_edit_button(call)
#
#
# @bot.callback_query_handler(func=lambda call: call.data in ['Назад', 'Создать объявление',
#                                                             'Посмотреть объявления'])
# def is_all_right_callback(call):
#     if call.data == 'Назад':
#         bot.set_state(call.from_user.id, state=OverallState.edit)
#         choose_edit_button(call)
#     elif call.data == 'Создать объявление':
#         add_post(call)
#     elif call.data == 'Посмотреть объявления':
#         edit_post(call)
