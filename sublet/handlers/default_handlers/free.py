from loader import bot
from utils.logger import logger
from states.overall import OverallState
from keyboards.reply.create_markup import create_markup
from keyboards.reply.calendar import show_calendar
from telebot.types import InputMediaPhoto
from pg_maker import get_active_sublets


@bot.message_handler(commands=['free'])
def free(message):
    bot.set_state(message.from_user.id, state=OverallState.free_dates)
    with bot.retrieve_data(message.from_user.id) as data:
        data['command'] = 'free'
    logger.warning(f'{message.from_user.username} — команда FREE')
    try:
        chat_id = message.message.chat.id
        message_id = message.message.message_id
        show_calendar(bot, message.message.chat.id, chat_id, message_id)
    except:
        show_calendar(bot, message.from_user.id)

@bot.message_handler(states=OverallState.free_show)
def show_variants(message):
    with bot.retrieve_data(message.from_user.id) as data:
        city = data['city']
        date = data['date_in']
    result = get_active_sublets(city, date)
    if result:
        for user_info, user_photos in result:
            media = []
            if user_photos:
                media.append(InputMediaPhoto(open(user_photos[0], 'rb').read(), caption=user_info))
                for photo_path in user_photos[1:]:
                    with open(photo_path, 'rb') as photo_file:
                        media.append(InputMediaPhoto(photo_file.read()))
            else:
                bot.send_message(message.from_user.id, "Фотографии не найдены")
                return
            try:
                bot.delete_message(message.message.chat.id, message.message.message_id)
            except:
                pass
            bot.send_media_group(message.from_user.id, media)
    else:
        buttons = [('⬇⬇⬇ Назад в меню ⬇⬇⬇', 'Назад в меню')]
        markup = create_markup(buttons)
        bot.edit_message_text('В эту дату пока нет ничего доступного',
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    bot.delete_state(message.from_user.id)

