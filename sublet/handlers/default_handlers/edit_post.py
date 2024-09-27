from loader import bot
from handlers.default_handlers.add_post import add_post
from pg_maker import (
    find_my_sublets,
    change_post,
    type_of_sublet,
    delete_post,
    status_of_sublet,
    update_photos,
    get_user_info_and_photos )
from keyboards.reply.create_markup import create_markup
from telebot.types import InputMediaPhoto
from states.overall import OverallState
from keyboards.reply.calendar import show_calendar
import os
import time
import threading


@bot.message_handler(commands=['edit_post'])
def edit_post(message):
    bot.delete_state(message.from_user.id)
    buttons = find_my_sublets(message.from_user.username)
    if buttons:
        buttons.append(('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню'))
        markup = create_markup(buttons)
        try:
            bot.edit_message_text("Какое объявление нужно отредактировать?",
                             message.message.chat.id, message.message.message_id, reply_markup=markup)
        except:
            bot.send_message(message.from_user.id, "Какое объявление нужно отредактировать?", reply_markup=markup)
    else:
        buttons = ([('Создать объявление', 'Создать объявление'),
                    ('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')])
        markup = create_markup(buttons)
        bot.edit_message_text("У вас пока нет объявлений",
                         message.message.chat.id, message.message.message_id, reply_markup=markup)


@bot.message_handler(state=OverallState.edit)
def choose_edit_button(message):
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
    try:
        lol = message.message.message_id
        bot.edit_message_text("Что хотите изменить?",
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Что хотите изменить?", reply_markup=markup)


@bot.message_handler(state=OverallState.change_type)
def change_type(message):
    all_types = ['Квартира', 'Комната']
    with bot.retrieve_data(message.from_user.id) as data:
        post_id = data['post_id']
    my_type = type_of_sublet(post_id)[0]
    all_types.remove(my_type)
    markup = create_markup([(f'Изменить на {all_types[0]}', f'Изменить на {all_types[0]}'),
                            ('⬇ Назад ⬇', 'Назад')])
    bot.edit_message_text(f'Сейчас выбран тип {my_type}',
                     message.message.chat.id, message.message.message_id, reply_markup=markup)


@bot.message_handler(state=OverallState.change_status)
def change_status(message):
    with bot.retrieve_data(message.from_user.id) as data:
        post_id = data['post_id']
    my_type = status_of_sublet(post_id)[0]
    if my_type:
        buttons = [('Отключить объявление', 'Изменить на отключено объявление'),
                   ('Назад', 'Назад')]
    else:
        buttons = [('Активировать объявление', 'Изменить на  активировано'),
                   ('Назад', 'Назад')]
    markup = create_markup(buttons)
    bot.edit_message_text(f'Сейчас объявление {"Активировано" if my_type else "Отключено"}',
                     message.message.chat.id, message.message.message_id, reply_markup=markup)


def change_address(message):
    bot.edit_message_text('Напишите новый адрес',
                          message.message.chat.id, message.message.message_id)
    bot.set_state(message.from_user.id, state=OverallState.edit_address)


@bot.message_handler(state=OverallState.edit_address)
def edit_address(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['new_address'] = message.text
        post_id = data['post_id']
    change_post(post_id=post_id, parameter_name='address', parameter=data['new_address'])
    bot.send_message(message.from_user.id, "Адрес изменен!")
    choose_edit_button(message)

def change_description(message):
    bot.edit_message_text('Введите новое описание', message.message.chat.id, message.message.message_id)
    bot.set_state(message.from_user.id, state=OverallState.edit_description)

@bot.message_handler(state=OverallState.edit_description)
def edit_description(message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['new_description'] = message.text
        post_id = data['post_id']
    change_post(post_id=post_id, parameter_name='description', parameter=data['new_description'])
    bot.send_message(message.from_user.id, "Описание изменено!")
    choose_edit_button(message)

def change_photos(message):
    bot.edit_message_text('Залейте новые фото вместо старых (все сразу, максимум 8 штук)',
                          message.message.chat.id, message.message.message_id)
    bot.set_state(message.from_user.id, state=OverallState.change_photos)
    with bot.retrieve_data(message.from_user.id) as data:
        data['photos'] = []

first_photo_time = {}

@bot.message_handler(content_types=['photo'], state=OverallState.change_photos)
def edit_photos(message):
    if message.from_user.id not in first_photo_time:
        first_photo_time[message.from_user.id] = time.time()
        threading.Timer(5, final_photo, args=(message,)).start()

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

def final_photo(message):
    first_photo_time.pop(message.from_user.id, None)
    with bot.retrieve_data(message.from_user.id) as data:
        post_id = data['post_id']
        update_photos(post_id, data['photos'])
    bot.send_message(message.from_user.id, 'Новые фото загружены')
    choose_edit_button(message)


@bot.message_handler(content_types=['text', 'document'], func=lambda message: True, state=OverallState.change_photos)
def handle_text_messages(message):
    if message.content_type == 'text':
        bot.reply_to(message, "Пожалуйста, отправьте фотографии.")
    elif message.content_type == 'document':
        bot.reply_to(message, "Пожалуйста, отправьте фотографии, а не документы.")


def see_post(message):
    media = []
    with bot.retrieve_data(message.from_user.id) as data:
        msg, user_photos = get_user_info_and_photos(data['post_id'])

    try:
        media.append(InputMediaPhoto(open(user_photos[0], 'rb').read(), caption=msg))
        for photo_path in user_photos[1:]:
            with open(photo_path, 'rb') as photo_file:
                media.append(InputMediaPhoto(photo_file.read()))
        try:
            bot.delete_message(message.message.chat.id, message.message.message_id)
        except:
            pass
        bot.send_media_group(message.from_user.id, media)
        buttons = [('Создать новое объявление', 'Создать объявление'),
                   ('⬇ Посмотреть все мои объявления ⬇', 'Посмотреть объявления'),
                   ('⬇⬇ Вернуться к этому объявлению ⬇⬇', 'Назад'),
                   ('⬇⬇⬇ Вернуться в меню ⬇⬇⬇', 'Назад в меню')]
        markup = create_markup(buttons)
        bot.send_message(message.from_user.id, 'Что дальше?', reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Загружены некорректные фото. Они должны быть в формате jpeg или png")
        return



# КНОПКИ С АДРЕСАМИ
@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def edit_post_callback(call):
    post_id = call.data
    bot.set_state(call.from_user.id, state=OverallState.edit)
    with bot.retrieve_data(call.from_user.id) as data:
        data['post_id'] = post_id
    choose_edit_button(call)


#КНОПКИ С ИЗМЕНЕНИЯМИ
@bot.callback_query_handler(func=lambda call: call.data.startswith('Изменить'))
def choose_buttons_callback(call):
    with bot.retrieve_data(call.from_user.id) as data:
        post_id = data['post_id']
    if call.data == 'Изменить тип саблета':
        change_type(call)
    elif call.data == 'Изменить адрес':
        change_address(call)
    elif call.data == 'Изменить описание':
        change_description(call)
    elif call.data == 'Изменить посмотреть пост':
        see_post(call)
    elif call.data == 'Изменить статус':
        change_status(call)
    elif call.data == 'Изменить фотографии':
        change_photos(call)
    elif call.data == 'Изменить удалить':
        try:
            delete_post(post_id)
            edit_post(call)
        except:
            bot.send_message(call.from_user.id, 'Что-то пошло не так. Возможно, пост уже удален?')
    elif call.data == 'Изменить даты':
        with bot.retrieve_data(call.from_user.id) as data:
            data['command'] = 'edit_post'
        show_calendar(bot, call.from_user.id)

    elif 'Изменить на' in call.data:
        if call.data == 'Изменить на отключено объявление':
            change_post(post_id=post_id, parameter_name='is_active', parameter=False)
        elif call.data == 'Изменить на  активировано':
            change_post(post_id=post_id, parameter_name='is_active', parameter=True)
        else:
            change_post(post_id=post_id, parameter_name='type', parameter=call.data.split()[2])
        choose_edit_button(call)


@bot.callback_query_handler(func=lambda call: call.data in ['Назад', 'Создать объявление',
                                                            'Посмотреть объявления'])
def is_all_right_callback(call):
    if call.data == 'Назад':
        bot.set_state(call.from_user.id, state=OverallState.edit)
        choose_edit_button(call)
    elif call.data == 'Создать объявление':
        add_post(call)
    elif call.data == 'Посмотреть объявления':
        edit_post(call)
