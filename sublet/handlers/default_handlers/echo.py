from telebot.types import Message
from loader import bot
from utils.logger import logger
from pg_maker import delete_table, all_users_from_db, get_active_sublets
from telebot.types import InputMediaPhoto


@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """ Вызывается, когда пользователь без состояния вводит несуществующую команду """
    all_users = all_users_from_db()

    if "ОБНОВИТЬ" in message.text:
        delete_table()
        bot.send_message(message.from_user.id, 'БД снесена')

    elif 'LOL' in message.text:
        result = get_active_sublets(flag='last_post')
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
            bot.send_media_group(message.from_user.id, media)

    elif message.text == 'ВСЕ':
        try:
            all_us = ", ".join([str(i[0]) for i in all_users])
            bot.send_message(message.from_user.id, all_us)
        except Exception as e:
            bot.send_message(message.from_user.id, str(e))

    else:
        logger.warning(f'{message.from_user.username} — ECHO — {message.text}')
        bot.reply_to(
            message, f"Такой команды нет: {message.text}\n"
                     f"Нажмите /start, чтобы посмотреть весь список команд"
        )

