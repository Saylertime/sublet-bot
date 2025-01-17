from states.overall import OverallState
from keyboards import all_cities, create_markup
from datetime import datetime

from pg_maker import get_active_sublets
from utils import show_post

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram_calendar import DialogCalendar

router_free = Router()


months_dict = {
    "Январь": "01",
    "Февраль": "02",
    "Март": "03",
    "Апрель": "04",
    "Май": "05",
    "Июнь": "06",
    "Июль": "07",
    "Август": "08",
    "Сентябрь": "09",
    "Октябрь": "10",
    "Ноябрь": "11",
    "Декабрь": "12",
}


@router_free.message(Command("free"))
@router_free.callback_query(F.data == "free")
async def free(message, state):
    await state.set_state(OverallState.free_dates)
    await state.update_data(offset=0, limit=5)

    buttons = [
        ("📅 В конкретную дату 📅", "Дата"),
        ("🏙️ Все объявления в городе 🏙️", "В городе"),
        ("🔎 Все доступные в определенном месяце 🔎", "Месяц"),
        ("🇮🇱 Все доступные саблеты во всех городах 🇮🇱", "Все сразу"),
        ("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"),
    ]
    markup = create_markup(buttons)
    msg = "Выберите вариант"

    if isinstance(message, CallbackQuery):
        message = message.message
        await message.edit_text(msg, reply_markup=markup)
    else:
        await message.answer(msg, reply_markup=markup)


@router_free.message(OverallState.free_show)
async def show_variants(message, state):
    data = await state.get_data()
    city = data["city"]
    by_what = data["by_what"]
    result = ""

    if by_what.strip() == "Дата":
        date = datetime.strptime(data["check_in"], "%Y-%m-%d")
        result = await get_active_sublets(flag="by_date", city=city, date=date)

    elif data["by_what"] == "Месяц":
        result = await get_active_sublets(
            flag="by_month", city=city, year=data["year"], month=data["month"]
        )

    elif data["by_what"] == "В городе":
        result = await get_active_sublets(flag="by_active", city=city)

    await send_sublets(result, message, state)


async def send_sublets(result, message, state):
    if result:

        for res in result:
            await show_post(message, result=res, flag="free")

        data = await state.get_data()
        city = data.get("city", "No city")

        if len(result) >= 5:
            markup = create_markup([("Показать ещё", f"load_more_{city}")])
            await message.message.answer("Хотите увидеть больше?", reply_markup=markup)

    else:
        buttons = [("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start")]
        markup = create_markup(buttons)
        msg = "В эту дату пока нет ничего доступного"
        try:
            await message.message.edit_text(msg, reply_markup=markup)
        except:
            await message.message.answer(msg, reply_markup=markup)
        await state.clear()


@router_free.callback_query(F.data == "Дата")
async def date_callback(message, state):
    await state.update_data(by_what="Дата", stage="finding", command="free")

    await message.message.edit_text(
        "Выберите дату заезда",
        reply_markup=await DialogCalendar().start_calendar(
            year=datetime.now().year, month=datetime.now().month
        ),
    )


@router_free.callback_query(F.data == "Месяц")
async def month_callback(message, state):
    await state.update_data(by_what="Месяц", command="free")
    buttons = []
    months = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]

    for month in months:
        buttons.append((month, f"month_{month}"))
    markup = create_markup(buttons)
    await message.message.edit_text("Выберите месяц:", reply_markup=markup)


@router_free.callback_query(F.data == "В городе")
async def city_callback(message, state):
    await state.update_data(by_what="В городе", command="free")
    await all_cities(message)


@router_free.callback_query(F.data == "Все сразу")
async def city_callback(message, state):
    await state.update_data(by_what="Все сразу", all=True)
    result = await get_active_sublets(flag="all_posts")
    if result:
        await send_sublets(result, message, state)


@router_free.callback_query(F.data.startswith("month_"))
async def startswith_month(message, state):
    month = message.data.split("_")[1] if message.data.startswith("month_") else None
    await state.update_data(month=int(months_dict[month]), command="free")
    buttons = []
    years = [str(year) for year in range(2025, 2028)]
    for year in years:
        buttons.append((year, f"year_{year}"))
    markup = create_markup(buttons)
    await message.message.edit_text(f"Выберите год:", reply_markup=markup)


@router_free.callback_query(F.data.startswith("year_"))
async def startswith_year(message, state):
    year = message.data.split("_")[1] if message.data.startswith("year_") else None
    await state.update_data(year=year)
    await all_cities(message)


@router_free.callback_query(F.data.startswith("load_more_"))
async def load_more_sublets(message, state):
    city = message.data.split("_")[2]
    data = await state.get_data()

    offset = data.get("offset", 5)
    new_offset = offset + 5
    await state.update_data(offset=new_offset)

    if city != "No city":
        result = await get_active_sublets(
            flag="by_active", city=city, offset=new_offset
        )
    else:
        result = await get_active_sublets(flag="all_posts", offset=new_offset)

    if result:
        await send_sublets(result, message, state)
    else:
        buttons = [("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start")]
        markup = create_markup(buttons)
        await message.message.edit_text(
            "Больше доступных объявлений нет ", reply_markup=markup
        )
