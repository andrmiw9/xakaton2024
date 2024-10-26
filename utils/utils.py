""" Различные вспомогательные функции """

from sys import stdout

import matplotlib.pyplot as plt
import rasterio
import torch
from colorama import Back
from loguru import logger


def tiff_to_tensor(tif_path):
    """
    Читает все каналы из файла.
    Обрезает верхнюю границу значений пикселей.
    Нормализация по текущему изображению.
    
    Parameters:
    - tif_path: Путь до изображения.
    
    Returns:
    - torch.Tensor: Обработанное изображение.
    """
    with rasterio.open(tif_path) as src:
        # Читаем все каналы изображения и преобразуем в numpy-массив
        img_array = src.read()  # Получаем массив с форматом (channels, height, width)
    img_tensor = torch.from_numpy(img_array).float()
    img_tensor = torch.clamp(img_tensor, min=0, max=5000)
    img_tensor = img_tensor / 5000
    return img_tensor


def plot_channels(img_tensor, rgb=None):
    """
    Визуализирует выбранные каналы тензора изображения.

    Parameters:
    - img_tensor (torch.Tensor): Тензор изображения с форматом (channels, height, width).
    - rgb (list of int): Индексы каналов, которые нужно визуализировать. По умолчанию [2, 1, 0].

    """
    # Проверяем, что в img_tensor достаточно каналов
    if rgb is None:
        rgb = [2, 1, 0]

    assert img_tensor.shape[0] > max(rgb), "Выбранные каналы отсутствуют в тензоре"

    # Извлекаем три выбранных канала и конвертируем их в numpy
    selected_channels = img_tensor[rgb].numpy()

    # Транспонируем из (channels, height, width) в (height, width, channels)
    if selected_channels.shape[0] == 3:
        selected_channels = selected_channels.transpose(1, 2, 0)
    else:
        raise ValueError("Должно быть выбрано ровно 3 канала для RGB изображения")

    # Отображаем изображение
    plt.figure(figsize=(20, 16))
    plt.imshow(selected_channels)
    plt.axis('off')
    plt.show()


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
