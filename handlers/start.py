from keyboards.reply.create_markup import create_markup
from handlers.add_post import add_post
from handlers.edit_post import edit_post
from handlers.free import free
from pg_maker import add_user

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, ContentType, InputMediaPhoto
from aiogram_calendar import DialogCalendar, DialogCalendarCallback

router_start = Router()


@router_start.message(CommandStart())
async def start_message(message, state):
    await add_user(message.from_user.username, str(message.from_user.id))
    await state.clear()

    buttons = [("🔎 Найти саблет 🔎", "Найти"),
               ("➕ Добавить объявление ➕", "Добавить"),
               ("🖊 Отредактировать объявление 🖊", "edit_post")]
    markup = create_markup(buttons)
    try:
        await message.edit_text("⬇⬇⬇ Добро пожаловать в САБЛЕТ-БОТ ⬇⬇⬇", reply_markup=markup)
    except:
        await message.answer("⬇⬇⬇ Добро пожаловать в САБЛЕТ-БОТ ⬇⬇⬇", reply_markup=markup)


# @router_start.callback_query(F.data == "edit_post")
# async def callback_find(message):
#     print('tyt')
#     await edit_post(message)

    #     'Добавить', 'Отредактировать', 'Назад в меню'
    # elif call.data == "Добавить":
    #     add_post(call)
    # elif call.data == "Отредактировать":
    #     edit_post(call)
    # elif call.data == 'Назад в меню':
    #     start_message(call)

