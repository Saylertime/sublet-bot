from aiogram import Router, F
from aiogram.types import Message, ContentType, InputMediaPhoto
from datetime import datetime
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
    get_user_locale
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, ContentType
from states.overall import OverallState
from time import sleep
import asyncio
from pg_maker import new_post, get_active_sublets


router_test = Router()


@router_test.message(Command("test"))
async def test_photo(message):
    result = await get_active_sublets(flag='last_post')
    media = [
        InputMediaPhoto(media=file_id, caption=result[0][0])
        if idx == 0 else InputMediaPhoto(media=file_id)
        for idx, file_id in enumerate(result[0][1])
    ]
    # media = [InputMediaPhoto(media=file_id) for file_id in result[0][1]]
    await message.answer_media_group(media)















# from datetime import datetime
# from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback, \
#     get_user_locale
# from aiogram import F, Router
# from aiogram.filters import Command
# from aiogram.filters.callback_data import CallbackData
# from aiogram.types import Message, CallbackQuery, ContentType
# from states.overall import OverallState
# from time import sleep
#
#
# router_test = Router()
#
#
# first_photo_time = {}
#
# @router_test.message(Command("test"))
# async def test_photo(message, state):
#     await state.set_state(OverallState.photos)
#     await message.answer("Кидай фото")
#
#
# @router_test.message(F.content_type == ContentType.PHOTO, OverallState.photos)
# async def photos(message, state):
#     data = await state.get_data()
#     photo_album = data.get("photo_album", [])
#
#     photo = message.photo[-1]
#     file_id = photo.file_id
#     photo_album.append(file_id)
#
#     await state.update_data(photo_album=photo_album)
#     await message.answer(f"Сейчас в альбоме: {len(photo_album)} фото.")
#
#     if len(photo_album) >= 8:
#         await state.set_state(OverallState.test1)
#         await final(message, state)
#
#
# @router_test.message(OverallState.test1)
# async def final(message, state):
#     data = await state.get_data()
#     photoss = data.get("photo_album", [])
#     print(str(photoss))
#     for photo in photoss:
#         await message.answer_photo(photo)





























# @router_test.message(Command("test"))
# async def test_func(message, state):
#     await dialog_check_in(message)
#     await state.update_data(stage="check_in")
#
#
# @router_test.message(OverallState.test1)
# async def dialog_check_in(message):
#     await message.answer(
#         "Выберите дату заезда",
#         reply_markup=await DialogCalendar().start_calendar(year=2025, month=1))
#
#
# @router_test.message(OverallState.test2)
# async def dialog_check_out(message, state):
#     await state.update_data(stage="check_out")
#     await message.answer(
#         "Выберите дату выезда",
#         reply_markup=await DialogCalendar().start_calendar(year=2025, month=1))
#
#
# @router_test.callback_query(DialogCalendarCallback.filter())
# async def process_dialog_calendar(callback_query, callback_data, state):
#     stage = (await state.get_data()).get("stage", "")
#     selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
#     if selected:
#         if stage == "check_in":
#             await state.update_data(check_in=date)
#             await callback_query.message.answer(
#                 f"Вы выбрали {date.strftime('%d.%m.%Y')}"
#             )
#             await dialog_check_out(callback_query.message, state)
#
#         elif stage == "check_out":
#
#             min_date = (await state.get_data()).get("check_in", "")
#
#             if min_date < date:
#                 await callback_query.message.answer(f"Вы выбрали {date.strftime('%d.%m.%Y')}")
#                 await state.update_data(check_out=date)
#             else:
#                 await callback_query.message.answer(
#                     f'Дата выезда ({date.strftime("%d.%m.%Y")}) '
#                     f'должна быть позже даты заезда ({min_date.strftime("%d.%m.%Y")})'
#                 )
#                 await dialog_check_out(callback_query.message, state)




# @router_test.message(F.text.lower() == 'navigation calendar')
# async def nav_cal_handler(message: Message):
#     await message.answer(
#         "Please select a date: ",
#         reply_markup=await SimpleCalendar().start_calendar()
#     )
#
#
# @router_test.message(F.text.lower() == 'navigation calendar w month')
# async def nav_cal_handler_date(message: Message):
#     calendar = SimpleCalendar(show_alerts=True)
#     calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
#     await message.answer(
#         "Calendar opened on feb 2023. Please select a date: ",
#         reply_markup=await calendar.start_calendar(year=2023, month=2)
#     )
#
#
# # simple calendar usage - filtering callbacks of calendar format
# @router_test.callback_query(SimpleCalendarCallback.filter())
# async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData):
#     calendar = SimpleCalendar(show_alerts=True)
#     calendar.set_dates_range(datetime(2025, 1, 1), datetime(2028, 12, 31))
#     selected, date = await calendar.process_selection(callback_query, callback_data)
#     if selected:
#         await callback_query.message.answer(
#             f'You selected {date.strftime("%d/%m/%Y")}'
#         )

#
# @router_test.message(F.text.lower() == 'dialog calendar')
# async def dialog_cal_handler(message: Message):
#     await message.answer(
#         "Please select a date: ",
#         reply_markup=await DialogCalendar().start_calendar()
#     )


# starting calendar with year 1989
# @router_test.message(F.text.lower() == 'dialog calendar w year')
# async def dialog_cal_handler_year(message: Message):
#     await message.answer(
#         "Выберите дату заезда ",
#         reply_markup=await DialogCalendar().start_calendar(2025))



