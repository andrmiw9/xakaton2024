"""
Модуль парсинг TOML конфиг и получает версию из файла в корне проекта.
Возвращает экземпляр настроек Settings (dict, 1-ый уровень вложенности) с помощью
кэшируемой (по модулям и совпадающим аргументам) функции get_settings()
"""

import os
import tomllib  # parse toml config
from functools import cache  # @cache decorator

from app.backend import constants
from app.backend.settings_model import Settings


@cache
def get_settings(_config_path: str = constants.DEFAULT_CONFIG_PATH,
                 _version_path: str = constants.VERSION_PATH) -> Settings:
    """
    Cacheable function (for each module actually runs only once) that returns dict of settings,
    read from .toml file and transformed into one - level dict.
    """

    if not _config_path:
        if os.name == 'nt':  # WINDOWS
            _config_path = constants.DEFAULT_CONFIG_PATH
        else:  # UNIX
            _config_path = constants.WAR_CONFIG_PATH

    config = Config(_config_path, _version_path)
    if config.settings.env_mode != 'PROD':
        print(f'Был зарегистрирован вызов get_settings(), cache info: {get_settings.cache_info()}')
    return config.settings


class ConfigError(OSError):
    """ Raised when smth in config.toml is wrong """
    pass


def load_toml(config_path: str, use_env: bool = False) -> dict:
    """ TOML config file related stuff """

    # путь переменной из окружения имеет приоритет (if use_env is True)
    env_var_name = 'XAKATON2024'
    if use_env and env_var_name in os.environ:
        config_path = os.environ[env_var_name]
        print(f"Переменная окружения {env_var_name} найдена, значение: {config_path}")

    if not os.path.isfile(config_path):  # если не валидный путь, то выйти
        print(f"Конфигурационный файл {config_path} не найден, выхожу...")
        # Raise error and just quit the app. There is no best solution here - the alternative would be to use
        # hard-coded values of settings
        raise FileNotFoundError

    print(f"Использую конфигурационный файл: {config_path}")
    config = {}
    with open(config_path, mode='rb') as f:  # binary mode is required for TOML, but it may be unsafe
        data = tomllib.load(f)
        # print("LOADED TOML", f"data: {data}")
        if data is None or len(data) == 0:
            raise ConfigError('Empty config!')

        config.update({k: v for subdict in data.values() for k, v in subdict.items()})

    # print("load_toml result", f"data: {config}")
    return config


class Config:
    """ Представляет обьект, парсящий настройки из TOML, версию и хранящий поле settings с полученными данными """

    def __init__(self, config_path: str = '', version_path: str = ''):
        # load to self.config dict of settings
        self.config = load_toml(config_path, use_env=True)

        # parse project version from version file and add to config
        self.config['version'] = self.get_project_version(version_path)

        # validate settings
        self.settings = Settings(**self.config)

    def get_project_version(self, version_file_path: str = '') -> str:
        """ Возврат номера версии приложения """
        if not version_file_path:
            # try to find version in project root. Mb actually unsafe
            version_file_path = os.path.join(self.settings.project_path, "../version")

        try:
            with open(version_file_path, "r") as file:
                version = file.readline().strip()
        except FileNotFoundError as fnfe:
            err = f"Ошибка: не найден файл с номером версии по пути: {version_file_path}. Ошибка: {fnfe}. Выхожу... "
            print(err)
            raise FileNotFoundError(err) from fnfe
        except Exception as e:  # jic
            err = f"Ошибка: {e}. Выхожу... "
            print(err)
            raise Exception(err) from e

        if version is None or version == '':
            err = f'Ошибка: найден файл {version_file_path}, но не найдена версия! Выхожу...'
            print(err)
            raise ValueError(err)

        print(f'Найден файл {version_file_path} с версией {version}. Без ошибок.')
        return version


if __name__ == '__main__':
    c = Config(config_path='configs/config.toml', version_path='backend_version')
    print(f'SETTINGS: {c.settings}')
