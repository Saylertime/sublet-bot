import aiofiles
from aiogram import Router, F
from pg_maker import add_cities, all_cities


router_echo = Router()


@router_echo.message(F.text.lower() == "история")
async def history_log(message):
    async with aiofiles.open("bot.log", mode="r") as file:
        lines = await file.readlines()
        filtered_lines = [line for line in lines if "@" in line and "история" not in line.lower()]
        msg = "\n".join(filtered_lines[-30:])
        await message.answer(f"{msg}")


@router_echo.message(F.text.startswith("ГОРОДА"))
async def add_city(message):
    cities = message.text.split(" ")[1:]
    for city in cities:
        await add_cities(city)
    msg = await all_cities()
    try:
        await message.answer(str(msg))
    except Exception as e:
        await message.answer(str(e))


@router_echo.message(~F.text.startswith("/"))
async def echo_echo(message):
    await message.reply(
        f"Такой команды нет: {message.text}\n"
        f"Нажмите /start, чтобы посмотреть весь список команд"
    )
