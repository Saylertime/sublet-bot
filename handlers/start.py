from config_data import config
from keyboards.create_markup import create_markup
from pg_maker import add_user

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

admins = config.ADMINS
router_start = Router()


@router_start.message(CommandStart())
@router_start.callback_query(F.data == "start")
async def start_message(event, state):
    await add_user(event.from_user.username, str(event.from_user.id))
    await state.clear()

    buttons = [
        ("🔎 Найти саблет 🔎", "free"),
        ("➕ Добавить объявление ➕", "add_post"),
        ("🖊 Отредактировать объявление 🖊", "edit_post"),
    ]
    if str(event.from_user.id) in admins:
        buttons.append(("ВСЁ", "lexa"))

    markup = create_markup(buttons)
    msg = "⬇⬇⬇ Добро пожаловать в САБЛЕТ-БОТ ⬇⬇⬇"

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(msg, reply_markup=markup)
    else:
        await event.answer(msg, reply_markup=markup)
