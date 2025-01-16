from config_data import config
from keyboards import create_markup_3_buttons

from aiogram.types import CallbackQuery


async def all_cities(message):
    if isinstance(message, CallbackQuery):
        message = message.message
    cities = config.CITIES
    buttons = [(city, city) for city in cities]
    markup = create_markup_3_buttons(buttons)
    msg = "Выберите город: "
    try:
        await message.edit_text(msg, reply_markup=markup)
    except Exception as e:
        print(e)
        await message.answer(msg, reply_markup=markup)
