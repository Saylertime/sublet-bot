from loader import bot
from utils.logger import logger
from states.overall import OverallState
from keyboards.reply.create_markup import create_markup
from keyboards.reply.calendar import show_calendar
from telebot.types import InputMediaPhoto
from pg_maker import get_active_sublets
from telebot import types


months_dict = {
    "Январь": "01",
    "Февраль": "02",
    "Март": "03",
    "Апрель": "04",
    "Май": "05",
    "Июнь": "06",
    "Июль": "07",
    "Август": "08",
    "Сентябрь": "09",
    "Октябрь": "10",
    "Ноябрь": "11",
    "Декабрь": "12"
}


@bot.message_handler(commands=['free'])
def free(message):
    bot.set_state(message.from_user.id, state=OverallState.free_dates)
    with bot.retrieve_data(message.from_user.id) as data:
        data['command'] = 'free'
        data['offset'] = 0
        data['limit'] = 5
    logger.warning(f'{message.from_user.username} — команда FREE')
    buttons = [('📅В конкретную дату📅', 'Дата'),
               ('🏙️Все объявления в городе🏙️', 'В городе'),
               ('🔎 Все доступные в определенном месяце 🔎', 'Месяц'),
               ('🇮🇱 Все доступные саблеты во всех городах 🇮🇱', 'Все сразу'),
               ('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
    markup = create_markup(buttons)
    try:
        bot.edit_message_text("Выберите вариант",
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "Выберите вариант", reply_markup=markup)


@bot.message_handler(states=OverallState.free_show)
def show_variants(message):
    with bot.retrieve_data(message.from_user.id) as data:
        city = data['city']

        if data['by_what'] == 'Дата':
            date = data['date_in']
            result = get_active_sublets(flag='by_date', city=city, date=date)

        elif data['by_what'] == 'Месяц':
            result = get_active_sublets(flag='by_month', city=city, year=data['year'], month=data['month'])

        elif data['by_what'] == 'В городе':
            result = get_active_sublets(flag='by_active', city=city)

    send_sublets(result, message)


def send_sublets(result, message):
    if result:
        try:
            bot.delete_message(message.message.chat.id, message.message.message_id)
        except Exception as e:
            print(e)

        for user_info, user_photos in result:
            media = []
            if user_photos:
                try:
                    with open(user_photos[0], 'rb') as photo_file:
                        media.append(types.InputMediaPhoto(photo_file.read(), caption=user_info))

                    for photo_path in user_photos[1:]:
                        with open(photo_path, 'rb') as photo_file:
                            media.append(types.InputMediaPhoto(photo_file.read()))
                except Exception as e:
                    print(e)
                    bot.send_message(message.from_user.id, "Не удалось загрузить фотографии. Убедитесь, что они в формате JPEG или PNG.")
                    continue

                try:
                    bot.send_media_group(message.from_user.id, media)
                except Exception as e:
                    print(e)
                    bot.send_message(message.from_user.id, "Не удалось отправить фотографии.")
                    continue
            else:
                bot.send_message(message.from_user.id, "Фотографии не найдены.")
                return

        try:
            with bot.retrieve_data(message.from_user.id) as data:
                city = data.get('city', 'No city')
        except Exception as e:
            print(e)
            city = 'No city'

        if len(result) >= 5:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Показать ещё", callback_data=f"load_more_{city}"))
            try:
                bot.send_message(message.from_user.id, "Хотите увидеть больше?", reply_markup=markup)
            except Exception as e:
                print(e)
    else:
        buttons = [('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
        markup = create_markup(buttons)

        try:
            bot.edit_message_text(
                "В эту дату пока нет ничего доступного",
                message.message.chat.id,
                message.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            print(e)
            try:
                bot.send_message(message.from_user.id, "В эту дату пока нет ничего доступного.", reply_markup=markup)
            except Exception as e:
                print(e)

        try:
            bot.delete_state(message.from_user.id)
        except Exception as e:
            print(e)


@bot.callback_query_handler(func=lambda call: call.data in ['Месяц', 'Дата', 'В городе', 'Все сразу'])
def callback_query_free(call):
    with bot.retrieve_data(call.from_user.id) as data:
        data['by_what'] = ''

    if call.data == 'Дата':
        data['by_what'] = 'Дата'
        try:
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            show_calendar(bot, call.message.chat.id, chat_id, message_id)
        except:
            show_calendar(bot, call.from_user.id)

    elif call.data == 'Месяц':
        data['by_what'] = 'Месяц'
        markup = types.InlineKeyboardMarkup()
        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        for month in months:
            markup.add(types.InlineKeyboardButton(month, callback_data=f"month_{month}"))
        bot.edit_message_text("Выберите месяц:", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)

    elif call.data =='В городе':
        data['by_what'] = 'В городе'
        buttons = [('Тель-Авив и окрестности', 'Тель-Авив',),
                   ('Хайфа', 'Хайфа')]
        markup = create_markup(buttons)
        bot.edit_message_text(f"Выберите город: ", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)

    elif call.data == 'Все сразу':
        result = get_active_sublets(flag='all_posts')
        data['all'] = True
        if result:
            send_sublets(result, call)


@bot.callback_query_handler(func=lambda call: call.data.startswith("month_") or call.data.startswith("year_"))
def callback_query_month(call):
    month = call.data.split("_")[1] if call.data.startswith("month_") else None
    year = call.data.split("_")[1] if call.data.startswith("year_") else None

    if month:
        with bot.retrieve_data(call.from_user.id) as data:
            data['month'] = int(months_dict[month])
        markup = types.InlineKeyboardMarkup()
        years = [str(year) for year in range(2024, 2027)]
        for year in years:
            markup.add(types.InlineKeyboardButton(year, callback_data=f"year_{year}"))
        bot.edit_message_text(f"Выберите год:", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)
    elif year:
        with bot.retrieve_data(call.from_user.id) as data:
            data['year'] = year
            buttons = [('Тель-Авив и окрестности', 'Тель-Авив',),
                       ('Хайфа', 'Хайфа')]
            markup = create_markup(buttons)
        bot.edit_message_text(f"Выберите город: ", chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("load_more_"))
def load_more_sublets(call):
    city = call.data.split('_')[2]
    with bot.retrieve_data(call.from_user.id) as data:
        data['offset'] += 5

    if city != 'No city':
        result = get_active_sublets(flag='by_active', city=city, offset=data['offset'])
    else:
        result = get_active_sublets(flag='all_posts', offset=data['offset'])

    if result:
        send_sublets(result, call)
    else:
        buttons = [('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
        markup = create_markup(buttons)
        try:
            bot.edit_message_text('Больше доступных объявлений нет ',
                                  call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.send_message(call.from_user.id, 'Пока нет ничего доступного', reply_markup=markup)
