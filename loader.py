from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from config_data import config

storage = RedisStorage.from_url(config.REDIS_URL)

bot = Bot(
    token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=storage)
