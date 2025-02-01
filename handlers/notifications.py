from states.overall import OverallState
from keyboards import all_cities, create_markup, make_buttons

from pg_maker import update_notifications, is_notifications_on

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

router_notifications = Router()


@router_notifications.message(Command("notifications"))
@router_notifications.callback_query(F.data == "notifications")
async def notifications(event, state):
    await state.set_state(OverallState.notifications)
    with_notifications = await is_notifications_on(str(event.from_user.id))
    buttons = [
        ("Включить по одному городу", "one_city_notifications"),
        ("Включить по всем городам", "all_cities_notifications"),
    ]
    if with_notifications:
        buttons.append(("Отключить уведомления", "turn_off_notifications"))
    buttons.append(("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"))
    markup = create_markup(buttons)
    msg = "Выберите вариант"

    if isinstance(event, CallbackQuery):
        message = event.message
        await message.edit_text(msg, reply_markup=markup)
    else:
        await event.answer(msg, reply_markup=markup)


@router_notifications.callback_query(F.data == "one_city_notifications")
async def city_notification(callback, state):
    await state.update_data(command="notifications")
    await all_cities(callback)


@router_notifications.callback_query(F.data == "all_cities_notifications")
async def all_cities_notification(callback, state):
    await state.clear()
    await update_notifications(city="ВСЕ", user_id=str(callback.from_user.id))
    await callback.message.edit_text(f"Включены уведомления по всем городам")
    await make_buttons(callback)


@router_notifications.callback_query(F.data == "turn_off_notifications")
async def turn_off_notifications(callback, state):
    await state.clear()
    await update_notifications(city="", user_id=str(callback.from_user.id))
    await notifications(callback, state)
    await callback.answer("Уведомления отключены!")
