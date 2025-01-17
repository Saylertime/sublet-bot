from states.overall import OverallState
from pg_maker import change_dates_pg
from handlers.edit_post import change_check_out
from handlers.add_post import check_out, handle_album_photo
from keyboards import all_cities, create_markup

from aiogram import Router
from aiogram_calendar import DialogCalendar, DialogCalendarCallback

from datetime import datetime

router_calendar = Router()


@router_calendar.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query, callback_data, state):
    stage = (await state.get_data()).get("stage", "")
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)

    if selected:
        if stage in ["check_in", "change_check_in"]:
            await state.update_data(check_in=date.strftime("%Y-%m-%d"))
            await callback_query.message.answer(f"Вы выбрали {date.strftime('%d.%m.%Y')}")

            if stage == "change_check_in":
                await change_check_out(callback_query.message, state)
            else:
                await check_out(callback_query.message, state, stage="check_out")

        elif stage in ["check_out", "change_check_out"]:
            min_date_str = (await state.get_data()).get("check_in", "")
            min_date = datetime.strptime(min_date_str, "%Y-%m-%d") if min_date_str else None

            print(stage)

            if min_date and min_date < date:
                await state.update_data(check_out=date.strftime("%Y-%m-%d"))
                await callback_query.message.answer(f"Вы выбрали {date.strftime('%d.%m.%Y')}\n")

                if stage == "change_check_out":
                    data = await state.get_data()
                    date_in = datetime.strptime(data["check_in"], "%Y-%m-%d")
                    date_out = datetime.strptime(data["check_out"], "%Y-%m-%d")
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
                    await callback_query.message.answer("Что дальше?", reply_markup=markup)

                elif stage == "check_out":
                    await state.set_state(OverallState.photos)
                    await callback_query.message.answer(f"Теперь загрузите фото (максимум — 8)")
                    await handle_album_photo(callback_query.message, state)
            else:
                await callback_query.message.answer(
                    f'Дата выезда ({date.strftime("%d.%m.%Y")}) '
                    f'должна быть позже даты заезда ({min_date.strftime("%d.%m.%Y")})'
                )
                await check_out(callback_query.message, state, stage=stage)

        elif stage == "finding":
            await state.update_data(check_in=date.strftime("%Y-%m-%d"))
            await all_cities(callback_query)
