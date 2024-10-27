"""
Pydantic модель, валидирующая конфиг и динамические
настройки (например версию проекта, которая подтягивается из файлика)
"""

from pydantic import BaseModel


class Settings(BaseModel):
    """ Модель pydantic, валидирующая конфиг """

    service_name: str = 'xakaton2024'  # захардкожено
    version: str  # из файла с версией в корне проекта (подтягивается в config.py)

    # формат и цвета логов
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>[<level>{level}</level>]" \
                      "<cyan>[{extra[object_id]}]</cyan>" \
                      "<magenta>{function}</magenta>:" \
                      "<cyan>{line}</cyan> - <level>{message}</level>"

    # app - общие настройки
    self_api_port: int = 7006  # порт для FastAPI сервера
    self_api_host: str = '0.0.0.0'  # адрес для FastAPI сервера
    env_mode: str = 'TEST'  # среда в которой запускается проект

    # logger - настройки логгера
    # уровень логирования. По умолчанию: TRACE если env_mode TEST, иначе DEBUG
    log_level: str | int = 10
