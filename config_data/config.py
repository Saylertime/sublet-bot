import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

LOCAL_ENV = os.getenv("LOCAL_ENV")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
REDIS_URL = os.getenv("REDIS_URL")
ADMINS = os.getenv("ADMINS").split(",")
CITIES = os.getenv("CITIES").split(", ")


DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("free", "Посмотреть доступные саблеты"),
    ("add_post", "Добавить объявление"),
    ("edit_post", "Редактировать объявление"),
)
