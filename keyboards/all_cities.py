from config_data import config
from keyboards import create_markup

from aiogram.types import CallbackQuery


async def all_cities(event):
    if isinstance(event, CallbackQuery):
        event = event.message
    cities = config.CITIES
    buttons = [(city, city) for city in cities]
    markup = create_markup(buttons, columns=3)
    msg = "Выберите город: "
    try:
        await event.edit_text(msg, reply_markup=markup)
    except Exception as e:
        print(e)
        await event.answer(msg, reply_markup=markup)
