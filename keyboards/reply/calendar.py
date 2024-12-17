from loader import bot
from telegram_bot_calendar import DetailedTelegramCalendar
from keyboards.reply.create_markup import create_markup
from states.overall import OverallState
from pg_maker import change_dates_pg
import datetime


def show_calendar(bot, from_user_id, chat_id='', message_id=''):
    """ Вызывает календарь """

    min_date = datetime.date.today()
    calendar, step = DetailedTelegramCalendar(locale='ru', min_date=min_date).build()
    if chat_id and message_id:
        bot.edit_message_text(f"Выберите дату", chat_id, message_id, reply_markup=calendar)
    else:
        bot.send_message(from_user_id, f"Выберите дату", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    """ Проверяет колбэк-дату и отправляет пользователя дальше """

    result, key, step = DetailedTelegramCalendar(locale='ru').process(c.data)

    with bot.retrieve_data(c.from_user.id) as data:
        if not result and key:
            bot.edit_message_text(f"Выберите возможную дату заезда",
                                  c.message.chat.id,
                                  c.message.message_id,
                                  reply_markup=key)

        elif result is not None and data.get('date_in') is None:
            bot.edit_message_text(f"Вы выбрали {result}",
                                  c.message.chat.id,
                                  c.message.message_id)
            data['date_in'] = result
            if data['command'] != 'free':
                bot.send_message(c.from_user.id, "Теперь выберите дату окончания саблета")
                show_calendar(bot, c.message.chat.id)

            else:
                buttons = [('Тель-Авив и окрестности', 'Тель-Авив',),
                           ('Хайфа', 'Хайфа')]
                markup = create_markup(buttons)
                bot.send_message(c.from_user.id, "Выберите город: ", reply_markup=markup)
                bot.set_state(c.from_user.id, state=OverallState.free_city)

        elif result is not None and data.get('date_in') is not None and data.get('date_out') is None:
            if result <= data['date_in']:
                bot.send_message(c.message.chat.id, 'Дата выезда должна быть позже заезда')
            else:
                data['date_out'] = result
                data['photos'] = []
                bot.edit_message_text(f"Вы выбрали период с {data['date_in']} по {data['date_out']}.",
                                      c.message.chat.id, c.message.message_id)
                if data['command'] == 'add_post':
                    bot.set_state(c.from_user.id, OverallState.photos)
                    bot.send_message(c.from_user.id, 'Загрузите фотографии в разрешении jpg или png (максимум 8). '
                                                     'Отправляйте все сразу, а не по одной ')
                elif data['command'] == 'edit_post':
                    buttons = [('Вернуться назад', 'Назад')]
                    markup = create_markup(buttons)
                    change_dates_pg(data['post_id'], data['date_in'], data['date_out'])
                    bot.send_message(c.from_user.id, f"Новые даты: {data['date_in']} — {data['date_out']}",
                                     reply_markup=markup)

