from aiogram.types import CallbackQuery, InputMediaPhoto
from loader import bot
from config_data import config


admins = config.ADMINS


async def show_post(message, result, flag="", is_admin=False):
    if isinstance(message, CallbackQuery):
        message = message.message
    description = result[0][0] if flag != "free" else result[0]
    photos = result[0][1] if flag != "free" else result[1]

    try:
        media = [
            (
                InputMediaPhoto(media=file_id, caption=description)
                if idx == 0
                else InputMediaPhoto(media=file_id)
            )
            for idx, file_id in enumerate(photos)
        ]
        await message.answer_media_group(media)
        if is_admin:
            for admin in admins:
                await bot.send_media_group(chat_id=admin, media=media)

    except Exception as e:
        print(e)
        media = [InputMediaPhoto(media=file_id) for file_id in photos]
        await message.answer_media_group(media)
        await message.answer(description)
        if is_admin:
            for admin in admins:
                await bot.send_media_group(chat_id=admin, media=media)
                await bot.send_message(chat_id=admin, text=description)


# async def make_post(all_info_and_photos):
#     sublets = []
#     for info_and_photos in all_info_and_photos:
#         if info_and_photos:
#             username, city, date_in, date_out, type, address, description, *photos = info_and_photos
#             f_date_in = date_in.strftime("%d-%m-%Y")
#             f_date_out = date_out.strftime("%d-%m-%Y")
#             user_info = f"🏠 Город: {city}\n🛌 Тип: {type}\n📬 Адрес: {address}\n" \
#                         f"📅 Свободные даты: \n{f_date_in} — {f_date_out}\n\n{description}\n\nОпубликовал: @{username}"
#             user_photos = [photo for photo in photos if photo is not None]
#             sublet = (user_info, user_photos)
#             sublets.append(sublet)
#     return sublets
