""" Основной файл запуска FastAPI """
import os.path

from datetime import datetime, timedelta

import loguru
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from loguru import logger
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from app.backend.config import get_settings
from app.backend.settings_model import Settings
from app.backend.utils import logger_set_up


def normal_app() -> FastAPI:
    """ FastAPI settings and endpoints. Mb move to class? """

    fastapi_app = FastAPI(version='0.0.1', title='Xakaton')

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
        logger.debug(f"Incoming request: /{''.join(str(request.url).split('/')[3:])}")
        # logger.debug(f"Incoming request route: {request.url.path}")
        response = await call_next(request)
        process_time = (datetime.now() - req_start_time)
        response.headers["X-Process-Time"] = str(process_time)
        logger.trace(f'Request time took {process_time} seconds')
        return response

    @fastapi_app.get("/")
    async def root() -> JSONResponse:  #
        """ Standard Hello World route """
        delta = datetime.now() - start_time
        if delta.days < 0:  # for midnight
            delta = timedelta(
                days=0,
                seconds=delta.seconds,
                microseconds=delta.microseconds
            )

        # uptime calculations
        td_sec = delta.seconds  # getting seconds field of the timedelta
        hour_count, rem = divmod(td_sec, 3600)  # calculating the total hours
        minute_count, second_count = divmod(rem, 60)  # distributing the remainders
        delta = f"{delta.days}:{hour_count}:{minute_count}:{second_count}"

        response = {
            "res": "ok",
            "app": f'{settings.service_name}',
            "version": f'{settings.version}',
            "uptime": delta
        }
        return JSONResponse(content=response,
                            status_code=200)

    @fastapi_app.post("/run_neuro")
    async def upload_image(file: UploadFile = File(...)):
        """ Ручка для посылки изображения на обработку нейросетью """
        # with open(f"uploads/{file.filename}", "wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)

        return {"filename": file.filename, "message": "Image uploaded successfully!"}

    @fastapi_app.get("/upload")
    async def upload_image():
        """ Ручка для посылки изображения на обработку нейросетью """
        # return FileResponse('../frontend/templates/v1.html')
        # _path = os.path.join(os.getcwd(), r'app\backend\frontend\templates\v1.html')
        # logger.trace(f'path: {_path}')
        return FileResponse('app/frontend/templates/v1.html')

    @fastapi_app.get("/config")
    async def config() -> Settings:
        """ Returns all settings of service. Work in TEST env_mode only! """

        if settings.env_mode == 'TEST':
            return settings
        else:
            msg = f'Unauthorized access to config'
            logger.warning(msg)
            raise HTTPException(status_code=403, detail=msg)  # 403 Forbidden

    @fastapi_app.exception_handler(404)
    async def custom_404_handler(request: Request, _):
        """ Собственный обработчик 404 ошибки """

        content = {
            "res": "Error",
            "msg": f"Not found {request.method} API handler for {request.url}"
        }
        logger.warning(f"content={content}")
        return JSONResponse(content=content,
                            status_code=404)

    return fastapi_app


def main():
    """ Initialize globals, such as settings and FastAPI app, do some preparations like logger bind and run uvicorn """

    global settings
    settings = get_settings()  # получаем настройки

    logger_set_up(settings)  # настройка логгера
    _logger: loguru.Logger = loguru.logger.bind(object_id='Run main')
    _logger.info(f'Logger up!')
    _logger.info("SETTINGS PARSED", f"data: {settings}")

    global app  # use global variable
    _logger.debug(f'Creating app...')
    app = normal_app()  # создаем FastAPI

    global start_time
    start_time = datetime.now()  # запоминаем время старта сервера

    try:
        # disabled duplicate logs (uvicorn logs)
        # uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
        # del uvicorn_log_config["loggers"]
        _logger.trace(f'Main passed, launching uvicorn...')

        uvicorn.run(app=f'__main__:app',
                    host=settings.self_api_host,
                    port=settings.self_api_port,
                    log_level="debug", access_log=False)

    except KeyboardInterrupt:
        logger.warning("KEYBOARD INTERRUPT MAIN")
    except Exception as e:
        logger.error("MAIN ERROR", f"e: {repr(e)}")


if __name__ == '__main__':
    start_time: datetime = None  # just time when service started
    settings: Settings = None  # app settings
    app: FastAPI = None
    main()
