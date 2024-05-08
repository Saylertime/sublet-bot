from telebot.types import Message
from loader import bot
from utils.logger import logger
from pg_maker import delete_table

@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """ Вызывается, когда пользователь без состояния вводит несуществующую команду """

    if "ОБНОВИТЬ" in message.text:
        delete_table()
        bot.send_message(message.from_user.id, 'БД снесена')


    else:
        logger.warning(f'{message.from_user.username} — ECHO — {message.text}')
        bot.reply_to(
            message, f"Такой команды нет: {message.text}\n"
                     f"Нажмите /start, чтобы посмотреть весь список команд"
        )

