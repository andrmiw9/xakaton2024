""" TODO """

from datetime import datetime

import loguru
import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.requests import Request

from utils import logger_set_up


def normal_app() -> FastAPI:
    """ FastAPI settings and endpoints. Mb move to class? """
    fastapi_app = FastAPI(version='0.0.1', title='Xakaton', docs_url=None, redoc_url=None)

    @fastapi_app.middleware('http')
    async def mdlwr(request: Request, call_next):
        """
        Middleware это предобработчик запросов
        :param request: Запрос входящий (или мб исходящий)
        :param call_next: Следующий ендпоинт, куда в оригинале шел запрос
        """

        logger: loguru.Logger = loguru.logger.bind(object_id='Middleware')
        req_start_time = datetime.now()
        # вывести адрес ручки без адреса и порта сервиса
        logger.info(f"Incoming request: /{''.join(str(request.url).split('/')[3:])}")
        response = await call_next(request)
        process_time = (datetime.now() - req_start_time)
        response.headers["X-Process-Time"] = str(process_time)
        logger.debug(f'Request time took {process_time} seconds')
        return response

    return fastapi_app


def main():
    global app
    logger_set_up()
    self_api_host: str = '0.0.0.0'  # fastapi address
    self_api_port: int = 7007  # fastapi port
    logger.info(f'Logger up!')
    logger.info(f'smth is running on {self_api_host}:{self_api_port}')

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
