from config_data import config
from keyboards.create_markup import create_markup
from pg_maker import add_user

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

router_start = Router()

admins = config.ADMINS

@router_start.message(CommandStart())
@router_start.callback_query(F.data == "start")
async def start_message(message, state):
    await add_user(message.from_user.username, str(message.from_user.id))
    await state.clear()

    buttons = [
        ("🔎 Найти саблет 🔎", "free"),
        ("➕ Добавить объявление ➕", "add_post"),
        ("🖊 Отредактировать объявление 🖊", "edit_post"),
    ]
    if str(message.from_user.id) in admins:
        buttons.append(("ВСЁ", "lexa"))
    markup = create_markup(buttons)
    msg = "⬇⬇⬇ Добро пожаловать в САБЛЕТ-БОТ ⬇⬇⬇"

    if isinstance(message, CallbackQuery):
        message = message.message
        await message.edit_text(msg, reply_markup=markup)
    else:
        await message.answer(msg, reply_markup=markup)
