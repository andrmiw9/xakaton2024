from sys import stdout

from colorama import Back
from loguru import logger

# формат и цвета логов
log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>[<level>{level}</level>]" \
                  "<cyan>[{extra[object_id]}]</cyan>" \
                  "<magenta>{function}</magenta>:" \
                  "<cyan>{line}</cyan> - <level>{message}</level>"


def logger_set_up():
    """ Loguru set up """

    logger.remove()  # this removes duplicates in the console if we use the custom log format
    logger.configure(extra={"object_id": "None"})  # Default values if not bind extra variable
    logger.level("HL", no=38, color=Back.MAGENTA, icon="🔺")
    logger.level(f"TRACE", color="<fg #1b7c80>")  # выставить цвет
    logger.level(f"SUCCESS", color="<bold><fg #2dd644>")  # выставить цвет

    # for output log in console
    logger.add(sink=stdout,
               format=log_format,
               colorize=True,
               enqueue=True,  # for better work of async
               level=1)
