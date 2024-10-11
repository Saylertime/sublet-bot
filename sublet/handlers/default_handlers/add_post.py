from loader import bot
from states.overall import OverallState
from utils.logger import logger
from pg_maker import new_post, get_active_sublets
from handlers.default_handlers.free import show_variants
import os
import time
import threading
from keyboards.reply.calendar import show_calendar
from keyboards.reply.create_markup import create_markup
from telebot.types import InputMediaPhoto


@bot.message_handler(commands=['add_post'])
def add_post(message):
    bot.delete_state(message.from_user.id)
    logger.warning(f'{message.from_user.username} — команда ADD_POST')

    bot.set_state(message.from_user.id, state=OverallState.add_post)
    if message.from_user.username is None:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите свой контакт или номер телефона. '
                                               'Эта информация будет указана в объявлении')
    else:
        start_post(message)

@bot.message_handler(state=OverallState.add_post)
def start_post(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['command'] = 'add_post'
        if message.from_user.username is None:
            data['contact'] = message.text
    buttons = [('Тель-Авив и окрестности', 'Тель-Авив',),
               ('Хайфа', 'Хайфа')]
    markup = create_markup(buttons)
    try:
        lol = message.message.message_id
        bot.edit_message_text("Выберите город: ",
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Выберите город: ", reply_markup=markup)


@bot.message_handler(state=OverallState.type)
def type_of_sublet(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['command'] = 'add_post'
    buttons = [('Квартира', 'Тип Квартира',),
               ('Комната', 'Тип Комната')]
    markup = create_markup(buttons)
    try:
        lol = message.message.message_id
        bot.edit_message_text("Выберите тип саблета: ",
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Выберите тип саблета: ", reply_markup=markup)


# КНОПОЧКИ
@bot.callback_query_handler(func=lambda call: call.data in ['Хайфа', 'Тель-Авив'])
def city_callback(call):
    with bot.retrieve_data(call.from_user.id) as data:
        data['city'] = call.data
        command = data['command']

    if command == 'add_post':
        bot.set_state(call.from_user.id, OverallState.type)
        type_of_sublet(call)

    elif command == 'free':
        bot.set_state(call.from_user.id, state=OverallState.free_show)
        show_variants(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('Тип'))
def type_of_sublet_callback(call):
    with bot.retrieve_data(call.from_user.id) as data:
        data['type'] = call.data.split()[1]
    bot.set_state(call.from_user.id, OverallState.address)
    address(call)

@bot.message_handler(state=OverallState.address)
def address(message):
    try:
        lol = message.message.message_id
        bot.edit_message_text("Напишите адрес: ",
                              message.message.chat.id, message.message.message_id)
    except:
        bot.send_message(message.from_user.id, 'Напишите адрес: ')
    bot.set_state(message.from_user.id, OverallState.description)


@bot.message_handler(state=OverallState.description)
def description(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['address'] = message.text
    bot.send_message(message.from_user.id, 'Опишите саблет. Здесь можно оставить свои контакты и добавить эмодзи 🏠')
    bot.set_state(message.from_user.id, OverallState.move_in)


@bot.message_handler(state=OverallState.move_in)
def move_in(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['description'] = message.text
    show_calendar(bot, message.from_user.id)

first_photo_time = {}


@bot.message_handler(content_types=['photo'], state=OverallState.photos)
def photos(message):
    if message.from_user.id not in first_photo_time:
        first_photo_time[message.from_user.id] = time.time()
        threading.Timer(5, final, args=(message,)).start()
    timestamp = int(time.time() * 1000)
    photo = message.photo[-1]

    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = f'photo_{message.from_user.id}_{message.date}_{timestamp}.jpg'
    filepath = os.path.join('media', filename)
    with open(filepath, 'wb') as new_file:
        new_file.write(downloaded_file)

    with bot.retrieve_data(message.from_user.id) as data:
        data['photos'].append(filepath)


def final(message):
    photo_variables = {}
    first_photo_time.pop(message.from_user.id, None)

    with bot.retrieve_data(message.from_user.id) as data:
        for i, photo_path in enumerate(data['photos'][:8]):
            photo_variables[f'photo{i + 1}'] = photo_path

        contact = message.from_user.username or data['contact']

        new_post(username=contact,
                 user_id=str(message.from_user.id),
                 city=data['city'],
                 address=data['address'],
                 type=data['type'],
                 description=data['description'],
                 date_in=data["date_in"],
                 date_out=data["date_out"],
                 **photo_variables)

    bot.delete_state(message.from_user.id)
    bot.send_message('68086662', f'Новый пост от {message.from_user.username}')
    result = get_active_sublets(flag='last_post')
    send_new_post_to_leha(result=result, user_id='68086662')


    buttons = [('Посмотреть или отредактировать мои объявления', 'Отредактировать'),
               ('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
    markup = create_markup(buttons)
    bot.send_message(message.from_user.id, 'Пост опубликован!!', reply_markup=markup)


@bot.message_handler(func=lambda message: True, state=OverallState.move_in)
def handle_text_in_move_in_state(message):
    bot.reply_to(message, "Пожалуйста, выберите дату в календаре.")

@bot.message_handler(content_types=['text', 'document'], func=lambda message: True, state=OverallState.photos)
def handle_text_messages(message):
    if message.content_type == 'text':
        bot.reply_to(message, "Пожалуйста, отправьте фотографии.")
    elif message.content_type == 'document':
        bot.reply_to(message, "Пожалуйста, отправьте фотографии, а не документы.")


def send_new_post_to_leha(result, user_id):
    try:
        for user_info, user_photos in result:
            media = []
            if user_photos:
                media.append(InputMediaPhoto(open(user_photos[0], 'rb').read(), caption=user_info))
                for photo_path in user_photos[1:]:
                    with open(photo_path, 'rb') as photo_file:
                        media.append(InputMediaPhoto(photo_file.read()))
            else:
                bot.send_message(user_id, "Фотографии не найдены")
                return
            bot.send_media_group(user_id, media)
    except Exception as e:
        bot.send_message(user_id, str(e))

