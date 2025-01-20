import logging
from datetime import datetime
import pytz


class MoscowTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        moscow_tz = pytz.timezone("Europe/Moscow")
        dt = datetime.fromtimestamp(record.created, tz=moscow_tz)
        return dt.strftime(datefmt or "%d-%m %H:%M")


class ExcludeErrorsFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        unwanted_phrases = [
            "Bad request syntax",
            "Bad HTTP/0.9 request type",
            "Invalid HTTP version",
            "aiohttp.http_exceptions.BadStatusLine",
            'can only concatenate str (not "NoneType") to str',
            "Invalid method encountered",
        ]
        return not any(phrase in message for phrase in unwanted_phrases)


logger = logging.getLogger()
logger.setLevel(logging.WARNING)

file_handler = logging.FileHandler("bot.log", mode="a")
file_handler.setFormatter(
    MoscowTimeFormatter(fmt="%(asctime)s - %(message)s", datefmt="%m-%d %H:%M")
)
file_handler.addFilter(ExcludeErrorsFilter())

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter(fmt="%(asctime)s - %(message)s", datefmt="%m-%d %H:%M")
)
console_handler.addFilter(ExcludeErrorsFilter())

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("aiogram").setLevel(logging.WARNING)

aiohttp_logger = logging.getLogger("aiohttp.server")
aiohttp_logger.setLevel(logging.ERROR)
aiohttp_logger.addFilter(ExcludeErrorsFilter())
aiohttp_logger.handlers.clear()
aiohttp_logger.addHandler(file_handler)
aiohttp_logger.addHandler(console_handler)
