""" Основной файл запуска FastAPI """

import cv2
import shutil

import os

import loguru
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.backend.config import get_settings
from app.backend.settings_model import Settings
from app.backend.utils import logger_set_up

from ultralytics import YOLO
import torch
import os
import numpy as np
import imagesize


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

    fastapi_app.mount("/uploads", StaticFiles(directory='uploads'), name="uploads")


    if os.name == 'nt':  # WINDOWS
        templates_dir = '../frontend/templates/'
    else:  # UNIX
        templates_dir = 'app/frontend/templates/'
    templates_dir = Jinja2Templates(directory="templates")

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

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

        try:
            file_path = os.path.join('uploads/', file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            if os.name == 'nt':  # WINDOWS
                model = YOLO('best.pt')
            else:  # UNIX
                model = YOLO('/home/user1/xakaton2024/yolo_pipeline/runs/segment/train3/weights/best.pt')

            # path = '/home/user1/xakaton2024/data/test_data/test_data_rgb/'

            results = model(file_path, save=True, save_txt=False, stream=True, retina_masks=True, conf=0.3, iou=0.8)

            for i, res in enumerate(results):
                for r in res:
                    try:
                        r = r[0]
                        masks = r.masks.data
                        boxes = r.boxes.data

                        # extract classes
                        clss = boxes[:, 5]

                        # get indices of results where class is 0 (people in COCO)
                        _indices = torch.where(clss == 1)

                        # use these indices to extract the relevant masks
                        _masks = masks[_indices]

                        # scale for visualizing results
                        _masks = torch.any(_masks, dim=0).int() * 255

                        # cv2.imshow(_masks.cpu().numpy())
                        # Преобразуем тензор в NumPy массив и отображаем его
                        masks_np = _masks.cpu().numpy()

                        # Проверяем размерность и добавляем размерность канала, если необходимо
                        if masks_np.ndim == 2:
                            masks_np = np.expand_dims(masks_np, axis=-1)  # Добавляем размерность для канала

                        # # Отображаем маску
                        # cv2.imshow(f'Mask {i}', masks_np)  # Передаем имя окна и массив изображения

                        mask_filename = f'mask_{file.filename}'
                        mask_path = os.path.join('masks/', mask_filename)
                        cv2.imwrite(mask_path, masks_np)  # Сохраняем маску

                        mask_url = f"/masks/{mask_filename}"  # URL для

                    except Exception as e:
                        logger.warning(f'WARN: {repr(e)}')
                        h, w = imagesize.get(file_path)

                        black_mask_rgb = np.zeros((w, h), dtype=np.uint8)
                        # cv2.imshow(black_mask_rgb)

                        # Создаем черную маску RGB
                        # black_mask_rgb = np.zeros((h, w, 3), dtype=np.uint8)  # Изменено на (h, w, 3) для RGB
                        cv2.imshow(f'Black Mask {i}', black_mask_rgb)  # Передаем имя окна для черной маски

            return {
                "filename": file.filename,
                "result": "ok",
                "message": "Image uploaded successfully!",
                "image_url": f"/uploads/{file.filename}"  # URL для доступа к изображению
            }

        except Exception as e:
            return {"filename": file.filename, "result": "error", "message": repr(e)}

    @fastapi_app.get("/upload")
    async def upload_image():
        """ Ручка для посылки изображения на обработку нейросетью """

        if os.name == 'nt':  # WINDOWS
            _path = '../frontend/templates/v2.html'
        else:  # UNIX
            _path = 'app/frontend/templates/v2.html'
        logger.trace(f'using path: {_path}')
        return FileResponse(_path)

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
