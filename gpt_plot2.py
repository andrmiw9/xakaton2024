import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_geom
from shapely import Point, Polygon

from user_settings import GJ_FILE, IMG2_FILE, IMG_FILE


def normalize(band):
    band_min, band_max = (band.min(), band.max())
    return (band - band_min) / (band_max - band_min)


def brighten(band):
    alpha = 0.13
    beta = 0
    return np.clip(alpha * band + beta, 0, 255)


def convert(im_path):
    with rasterio.open(im_path) as fin:
        raster_bounds = fin.bounds
        print(f'raster bounds (geo coordinates): {raster_bounds}')

        red = fin.read(3)
        green = fin.read(2)
        blue = fin.read(1)
        print(f'fin: {fin}')
        print(f'fin meta: {fin.meta}')
        print(f'fin crs: {fin.crs}')
        # Получаем трансформацию
        transform = fin.transform
        print(f'fin transform: {transform}')
        # Пример: получение географических координат для пикселя (x, y)
        x_pixel, y_pixel = 100, 100  # Индексы пикселей
        x_geo, y_geo = transform * (x_pixel, y_pixel)
        print(f'x_geo, y_geo: {x_geo, y_geo}')
        pixel_size_x, pixel_size_y = fin.res
        print(f"Pixel size X: {pixel_size_x}, Pixel size Y: {pixel_size_y}")

    red_b = brighten(red)
    green_b = brighten(green)
    blue_b = brighten(blue)

    red_bn = normalize(red_b)
    green_bn = normalize(green_b)
    blue_bn = normalize(blue_b)

    # Создание RGB изображения
    img = np.dstack((red_bn, green_bn, blue_bn))
    return img


def plot_data(image_path, geojson_path):
    img = convert(image_path)  # Получаем растровое изображение

    # Чтение GeoJSON файла
    gdf = gpd.read_file(geojson_path)
    # gdf = gdf.to_crs(4326)
    gdf.tags.unique()
    # Проверка CRS и установка, если необходимо
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
        print(f'GDF CRS IS NONE! Setting to 4326!')
    else:
        print(f'GDF CRS is not None!: {gdf.crs}')

    print("GeoDataFrame total bounds:", gdf.total_bounds)

    # Убедитесь, что у вас есть колонка с геометрией
    if 'geometry' not in gdf.columns:
        raise ValueError("GeoDataFrame does not contain a 'geometry' column.")
    else:
        print(f"GeoDataFrame contains a 'geometry' column: {gdf['geometry'][0]} and so on...")

    # Установите активную геометрию
    gdf.set_geometry('geometry', inplace=True)

    # # Определите параметры трансформации
    pixel_size_x = 0.0001459
    pixel_size_y = 0.0000879
    # замените pixel_size_x и pixel_size_y на реальные значения
    _transform = from_origin(58.53,
                             51.22,
                             pixel_size_x,
                             pixel_size_y)

    # Применение трансформации к геометрии
    def transform_geometry(geom):
        if geom.is_empty:
            return geom

        if isinstance(geom, Point):
            return Point(_transform * (geom.x, geom.y))

        elif isinstance(geom, Polygon):
            # Получаем координаты внешней границы полигона
            x, y = geom.exterior.xy
            transformed_points = [_transform * (xi, yi) for xi, yi in zip(x, y)]
            # Создаем новый полигон из трансформированных точек
            return Polygon(transformed_points)

        # Добавьте обработку других типов геометрии, если это необходимо
        return geom  # Возвращаем оригинальную геометрию, если тип не поддерживается

    # gdf['geometry'] = gdf['geometry'].apply(transform_geometry)

    # # Преобразуйте геометрию в соответствии с трансформацией
    # gdf['geometry'] = gdf['geometry'].apply(lambda geom: transform_geom(_transform, geom))

    # Преобразуйте геометрию в соответствии с трансформацией
    # gdf['geometry'] = gdf['geometry'].apply(lambda geom: transform_geom('EPSG:4326', 'EPSG:3857', geom))

    # Сравнение границ
    print("GeoDataFrame total bounds after convert:", gdf.total_bounds)

    # Создание фигуры и осей
    fig, ax = plt.subplots(figsize=(12, 12))

    # Отображение растрового изображения
    ax.imshow(img, extent=[-180, 180, -90, 90])  # Замените на ваши реальные координаты

    # Отображение векторных данных
    gdf.plot(ax=ax, edgecolor='red', linewidth=2)  # Красные контуры для векторных данных

    # print(f'gdf head: {gdf.head()}')

    # Настройка графика
    ax.set_title('Raster and GeoJSON Overlay')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()


def plot_data2(image_path, geojson_path):
    # Получаем растровое изображение
    img = convert(image_path)

    # Чтение GeoJSON файла
    gdf = gpd.read_file(geojson_path)

    # Получение CRS растрового изображения
    with rasterio.open(image_path) as src:
        raster_crs = src.crs

    # Приведение GeoDataFrame к CRS растрового изображения
    if gdf.crs != raster_crs:
        gdf = gdf.to_crs(raster_crs)

    # Создание фигуры и осей
    fig, ax = plt.subplots(figsize=(12, 12))

    # Отображение растрового изображения
    ax.imshow(img, extent=[-180, 180, -90, 90])  # Замените на ваши реальные координаты

    # Отображение векторных данных
    gdf.plot(ax=ax, edgecolor='blue', linewidth=2, facecolor='none')  # Измените цвет и толщину

    # Настройка графика
    ax.set_title('Raster and GeoJSON Overlay')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    plot_data(IMG_FILE, GJ_FILE)
    # plot_data2(IMG_FILE, GJ_FILE)
    # print(type(IMG2_FILE))
