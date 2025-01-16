from states.overall import OverallState
from pg_maker import change_dates_pg
from handlers.edit_post import change_check_out
from handlers.add_post import check_out, handle_album_photo
from keyboards import all_cities, create_markup

from aiogram import Router
from aiogram_calendar import DialogCalendar, DialogCalendarCallback

router_calendar = Router()


@router_calendar.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query, callback_data, state):
    stage = (await state.get_data()).get("stage", "")
    selected, date = await DialogCalendar().process_selection(
        callback_query, callback_data
    )
    if selected:
        if stage == "check_in" or stage == "change_check_in":
            await state.update_data(check_in=date)
            await callback_query.message.answer(
                f"Вы выбрали {date.strftime('%d.%m.%Y')}"
            )
            if stage == "change_check_in":
                await change_check_out(callback_query.message, state)
            else:
                await check_out(callback_query.message, state)

        elif stage == "check_out" or stage == "change_check_out":
            min_date = (await state.get_data()).get("check_in", "")

            if min_date < date:
                await state.update_data(check_out=date)
                await state.set_state(OverallState.photos)
                await callback_query.message.answer(
                    f"Вы выбрали {date.strftime('%d.%m.%Y')}.\n"
                )
                if stage == "change_check_out":
                    data = await state.get_data()
                    date_in = data["check_in"]
                    date_out = data["check_out"]
                    post_id = int(data["post_id"])
                    await change_dates_pg(date_in, date_out, post_id)
                    await callback_query.message.answer("Даты изменены!")
                    buttons = [
                        ("➕ Создать новое объявление ➕", "add_post"),
                        ("⬇ Вернуться к этому объявлению ⬇", "Назад"),
                        ("⬇⬇ Посмотреть все мои объявления ⬇⬇", "edit_post"),
                        ("⬇⬇⬇ Вернуться в меню ⬇⬇⬇", "start"),
                    ]
                    markup = create_markup(buttons)
                    await callback_query.message.answer(
                        "Что дальше?", reply_markup=markup
                    )

                else:
                    await callback_query.message.answer(
                        f"Теперь загрузите фото (максимум — 8)"
                    )
                    await handle_album_photo(callback_query.message, state)
            else:
                await callback_query.message.answer(
                    f'Дата выезда ({date.strftime("%d.%m.%Y")}) '
                    f'должна быть позже даты заезда ({min_date.strftime("%d.%m.%Y")})'
                )
                await check_out(callback_query.message, state)

        elif stage == "finding":
            await state.update_data(check_in=date)
            await all_cities(callback_query)
