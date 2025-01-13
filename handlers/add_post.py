from states.overall import OverallState
from pg_maker import new_post, get_active_sublets
# from handlers.free import show_variants
import asyncio

from keyboards.reply.create_markup import create_markup

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ContentType, InputMediaPhoto
from aiogram_calendar import DialogCalendar, DialogCalendarCallback

router_add_post = Router()


@router_add_post.message(Command("add_post"))
@router_add_post.callback_query(F.data == "add_post")
async def add_post(message, state):
    await state.set_state(OverallState.add_post)
    name = message.from_user.username
    if isinstance(message, CallbackQuery):
        message = message.message

    if not name:
        await message.answer("Пожалуйста, введите свой контакт или номер телефона. "
                             "Эта информация будет указана в объявлении")
    else:
        await start_post(message, state)


@router_add_post.message(OverallState.add_post)
async def start_post(message, state):
    await state.update_data(command="add_post")
    if message.from_user.username is None:
        await state.update_data(contact=message.text)
    buttons = [("Тель-Авив и окрестности", "Тель-Авив",),
               ("Хайфа", "Хайфа")]
    markup = create_markup(buttons)
    try:
        await message.reply("Выберите город: ",
                              message.message_id, reply_markup=markup)
    except:
        await message.answer("Выберите город: ", reply_markup=markup)


@router_add_post.callback_query(F.data.in_({"Тель-Авив", "Хайфа"}))
async def city_callback(message, state):
    await state.update_data(city=message.data)
    command = (await state.get_data()).get("command", "")
    if command == "add_post":
        await state.set_state(OverallState.type)
        await type_of_sublet(message.message, state)

    elif command == "free":
        await state.set_state(OverallState.free_show)
        # await show_variants(message)


@router_add_post.message(OverallState.type)
async def type_of_sublet(message, state):
    buttons = [("Квартира", "Тип Квартира",),
               ("Комната", "Тип Комната")]
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
    await message.answer("Опишите саблет. Здесь можно оставить свои контакты и добавить эмодзи 🏠\n\n"
                         "ВНИМАНИЕ: максимальная длина сообщения — 400 символов")
    await state.set_state(OverallState.check_in)


@router_add_post.message(OverallState.check_in)
async def check_in(message, state):
    if len(message.text) < 400:
        await state.update_data(description=message.text,
                                stage="check_in")
        await message.answer(
            "Выберите дату заезда",
            reply_markup=await DialogCalendar().start_calendar(year=2025, month=1))
    else:
        await message.answer("Описание слишком длинное. Сократите его до 400 знаков и попробуйте еще раз")


@router_add_post.message(OverallState.check_out)
async def check_out(message, state):
    await state.update_data(stage="check_out")
    await message.answer(
        "Выберите дату выезда",
        reply_markup=await DialogCalendar().start_calendar(year=2025, month=1))


@router_add_post.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query, callback_data, state):
    stage = (await state.get_data()).get("stage", "")
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        if stage == "check_in":
            await state.update_data(check_in=date)
            await callback_query.message.answer(
                f"Вы выбрали {date.strftime('%d.%m.%Y')}"
            )
            await check_out(callback_query.message, state)

        elif stage == "check_out":
            min_date = (await state.get_data()).get("check_in", "")

            if min_date < date:
                await state.update_data(check_out=date)
                await state.set_state(OverallState.photos)
                await callback_query.message.answer(f"Вы выбрали {date.strftime('%d.%m.%Y')}.\n"
                                                    f"Теперь загрузите фото (максимум — 8")
                await handle_album_photo(callback_query.message, state)
            else:
                await callback_query.message.answer(
                    f'Дата выезда ({date.strftime("%d.%m.%Y")}) ' 
                    f'должна быть позже даты заезда ({min_date.strftime("%d.%m.%Y")})'
                )
                await check_out(callback_query.message, state)


media_groups = {}
timers = {}
MAX_PHOTOS = 8


@router_add_post.message(F.media_group_id, F.content_type == ContentType.PHOTO, OverallState.photos)
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
        await final(message, state)


async def final(message, state):
    data = await state.get_data()
    contact = message.from_user.username or data['contact']
    try:
        await new_post(
            username=contact,
            user_id=str(message.from_user.id),
            city=data['city'],
            address=data['address'],
            type=data['type'],
            description=data['description'],
            date_in=data["check_in"],
            date_out=data["check_out"],
            photos=data.get("photos", [])
        )

        result = await get_active_sublets(flag="last_post")
        await show_post(message, result)
    except Exception as e:
        await message.answer(str(e))


async def show_post(message, result):
    media = [
        InputMediaPhoto(media=file_id, caption=result[0][0])
        if idx == 0 else InputMediaPhoto(media=file_id)
        for idx, file_id in enumerate(result[0][1])
    ]
    await message.answer_media_group(media)




#
# def final(message):
#     photo_variables = {}
#     first_photo_time.pop(message.from_user.id, None)
#
#     with bot.retrieve_data(message.from_user.id) as data:
#         for i, photo_path in enumerate(data['photos'][:8]):
#             photo_variables[f'photo{i + 1}'] = photo_path
#
#         contact = message.from_user.username or data['contact']
#
#         new_post(username=contact,
#                  user_id=str(message.from_user.id),
#                  city=data['city'],
#                  address=data['address'],
#                  type=data['type'],
#                  description=data['description'],
#                  date_in=data["date_in"],
#                  date_out=data["date_out"],
#                  **photo_variables)
#
#     bot.delete_state(message.from_user.id)
#     bot.send_message('68086662', f'Новый пост от {message.from_user.username}')
#     result = get_active_sublets(flag='last_post')
#     send_new_post_to_leha(result=result, user_id='68086662')
#
#
#     buttons = [('Посмотреть или отредактировать мои объявления', 'Отредактировать'),
#                ('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
#     markup = create_markup(buttons)
#     bot.send_message(message.from_user.id, 'Пост опубликован!!', reply_markup=markup)
#
#
# @bot.message_handler(func=lambda message: True, state=OverallState.move_in)
# def handle_text_in_move_in_state(message):
#     bot.reply_to(message, "Пожалуйста, выберите дату в календаре.")
#
# @bot.message_handler(content_types=['text', 'document'], func=lambda message: True, state=OverallState.photos)
# def handle_text_messages(message):
#     if message.content_type == 'text':
#         bot.reply_to(message, "Пожалуйста, отправьте фотографии.")
#     elif message.content_type == 'document':
#         bot.reply_to(message, "Пожалуйста, отправьте фотографии, а не документы.")
#
#
# def send_new_post_to_leha(result, user_id):
#     try:
#         for user_info, user_photos in result:
#             media = []
#             if user_photos:
#                 media.append(InputMediaPhoto(open(user_photos[0], 'rb').read(), caption=user_info))
#                 for photo_path in user_photos[1:]:
#                     with open(photo_path, 'rb') as photo_file:
#                         media.append(InputMediaPhoto(photo_file.read()))
#             else:
#                 bot.send_message(user_id, "Фотографии не найдены")
#                 return
#             bot.send_media_group(user_id, media)
#     except Exception as e:
#         bot.send_message(user_id, str(e))
#
