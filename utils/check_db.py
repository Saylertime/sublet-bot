from pg_maker import deactivate_active_sublets
from loader import bot
from keyboards import create_markup

from datetime import datetime


async def deactivate_old_sublets():
    date = datetime.now()
    all_sublets = await deactivate_active_sublets(date)
    buttons = [
        ("Посмотреть или отредактировать мои объявления", "edit_post"),
        ("⬇⬇⬇ Назад в меню ⬇⬇⬇", "start"),
    ]
    markup = create_markup(buttons)
    count = 0

    for sub in all_sublets:
        count += 1
        user_id, address = sub["user_id"], sub["address"]
        await bot.send_message(
            chat_id=user_id,
            text=f"Саблет по адресу '{address}' деактивирован. "
            f"Не забудьте его продлить и заново активировать, если хотите, чтобы другие пользователи его видели",
            reply_markup=markup,
        )
    await bot.send_message(
        chat_id=68086662, text=f"Почистили базу. Деактивировали {count} объявлений"
    )
