from loader import bot
from keyboards.reply.create_markup import create_markup
from utils.logger import logger
from handlers.default_handlers.add_post import add_post
from handlers.default_handlers.edit_post import edit_post
from handlers.default_handlers.free import free


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.delete_state(message.from_user.id)
    logger.warning(f'{message.from_user.username} — команда START')
    buttons = [('Найти саблет', 'Найти'),
               ('Добавить объявление', 'Добавить'),
               ('Отредактировать объявление', 'Отредактировать')]
    markup = create_markup(buttons)
    try:
        lol = message.message.message_id
        bot.edit_message_text("⬇⬇⬇ Добро пожаловать в САБЛЕТ-БОТ ⬇⬇⬇",
                              message.message.chat.id, message.message.message_id, reply_markup=markup)
    except:
        bot.send_message(message.from_user.id, "⬇⬇⬇ Добро пожаловать в САБЛЕТ-БОТ ⬇⬇⬇", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['Найти', 'Добавить', 'Отредактировать', 'Назад в меню'])
def callback_query_start(call):
    if call.data == 'Найти':
        free(call)
    elif call.data == "Добавить":
        add_post(call)
    elif call.data == "Отредактировать":
        edit_post(call)
    elif call.data == 'Назад в меню':
        start_message(call)

