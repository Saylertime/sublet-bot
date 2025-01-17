import logging

logging.basicConfig(
    filename="bot.log",
    filemode="a",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%m %H:%M",
    level=logging.WARNING,
)

logger = logging.getLogger()
