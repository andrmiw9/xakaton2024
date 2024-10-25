from sys import stdout

import uvicorn
from colorama import Back
from fastapi import FastAPI
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


def main():
    global app
    logger_set_up()
    self_api_host: str = '0.0.0.0'  # fastapi address
    self_api_port: int = 7007  # fastapi port
    logger.info(f'Logger up!')
    logger.info(f'smth is running on {self_api_host}:{self_api_port}')

    app = FastAPI(
        title=f"smth",
        version='0.0.1',
        description=f"Documentation for smth:0.0.1",
        docs_url="/"
    )

    try:
        # disabled duplicate logs (uvicorn logs)
        # uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        # del uvicorn_log_config["loggers"]

        uvicorn.run(app=f'__main__:app',
                    host=self_api_host,
                    port=self_api_port,
                    log_level="debug", access_log=False)

    except KeyboardInterrupt:
        logger.warning("KEYBOARD INTERRUPT MAIN")
    except Exception as e:
        logger.error("MAIN ERROR", f"e: {repr(e)}")


if __name__ == '__main__':
    app: FastAPI = None
    main()
