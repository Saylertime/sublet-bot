import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config_data import config
from handlers import routers
from loader import bot, dp
from middlewares.logging_middleware import LoggingMiddleware


LOCAL_ENV = config.LOCAL_ENV
BASE_URL = "https://glinkin.pro"
BOT_TOKEN = config.BOT_TOKEN
WEBHOOK_PATH = "/webhook_sublet"
PORT = 5004
HOST = "0.0.0.0"


# Функция для установки командного меню для бота
async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [
        BotCommand(command=cmd, description=desc)
        for cmd, desc in config.DEFAULT_COMMANDS
    ]
    # Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


# Функция, которая будет вызвана при запуске бота
async def on_startup() -> None:
    # Устанавливаем командное меню
    await set_commands()
    # Устанавливаем вебхук для приема сообщений через заданный URL
    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")
    await bot.send_message(chat_id=68086662, text="Бот запущен на вебхуках!")


# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:
    await bot.send_message(chat_id=68086662, text="Бот остановлен!")
    # Удаляем вебхук и, при необходимости, очищаем ожидающие обновления
    await bot.delete_webhook(drop_pending_updates=True)
    # Закрываем сессию бота, освобождая ресурсы
    await bot.session.close()


# Основная функция, которая запускает приложение
def main_webhook() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    for router in routers:
        dp.include_router(router)

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)

    # Создаем веб-приложение на базе aiohttp
    app = web.Application()

    # Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot  # Передаем диспетчер  # Передаем объект бота
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    web.run_app(app, host=HOST, port=PORT)


async def main():
    await set_commands()
    for router in routers:
        dp.include_router(router)

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(chat_id=68086662, text="Бот запущен локально!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    if LOCAL_ENV == "local":
        asyncio.run(main())
    else:
        main_webhook()
