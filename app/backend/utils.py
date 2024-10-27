""" Вспомогательные функции """

from sys import stdout

from colorama import Back
from loguru import logger

from app.backend.settings_model import Settings


def logger_set_up(_settings: Settings):
    """ Loguru set up """

    logger.remove()  # this removes duplicates in the console if we use the custom log format
    logger.configure(extra={"object_id": "None"})  # Default values if not bind extra variable
    logger.level("HL", no=38, color=Back.MAGENTA, icon="🔺")
    logger.level(f"TRACE", color="<fg #1b7c80>")  # выставить цвет
    logger.level(f"SUCCESS", color="<bold><fg #2dd644>")  # выставить цвет

    # Sink  for output log in console
    logger.add(sink=stdout,
               format=_settings.log_format,
               colorize=True,
               enqueue=True,  # for better work of async
               level=_settings.log_level)  # mb backtrace=True?
