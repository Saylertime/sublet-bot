from aiogram.types import CallbackQuery, InputMediaPhoto
from loader import bot
from config_data import config

admins = config.ADMINS


async def show_post(
    event, result, flag="", is_admin=False, users_for_notifications=None
):
    if isinstance(event, CallbackQuery):
        event = event.message
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
        await event.answer_media_group(media)

        if is_admin:
            await send_to_users(admins, description, media, is_admin=True)
        if users_for_notifications:
            await send_to_users(users_for_notifications, description, media)

    except Exception as e:
        print(e)
        media = [InputMediaPhoto(media=file_id) for file_id in photos]
        await event.answer_media_group(media)
        await event.answer(description)


async def send_to_users(users, description, media, is_admin=False):
    for user in users:
        try:
            await bot.send_media_group(chat_id=user, media=media)
        except Exception as e:
            print(str(e))
            await bot.send_media_group(chat_id=user, media=media)
            await bot.send_message(chat_id=user, text=description)
            if is_admin:
                await bot.send_message(chat_id=user, text=str(e))


async def make_post(all_info_and_photos):
    sublets = []
    for info_and_photos in all_info_and_photos:
        if info_and_photos:
            username, city, date_in, date_out, type, address, description, *photos = (
                info_and_photos
            )
            f_date_in = date_in.strftime("%d-%m-%Y")
            f_date_out = date_out.strftime("%d-%m-%Y")
            user_info = (
                f"🏠 Город: {city}\n🛌 Тип: {type}\n📬 Адрес: {address}\n"
                f"📅 Свободные даты: \n{f_date_in} — {f_date_out}\n\n{description}\n\nОпубликовал: @{username}"
            )
            user_photos = [photo for photo in photos if photo is not None]
            sublet = (user_info, user_photos)
            sublets.append(sublet)
    return sublets
