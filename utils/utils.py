""" Различные вспомогательные функции """

import matplotlib.pyplot as plt
import rasterio
import torch


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
