import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from geopandas import GeoDataFrame
from rasterio.plot import show
from rasterio.transform import from_origin

from user_settings import GJ_FILE, IMG_FILE
from loguru import logger
from utils import logger_set_up


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
        logger.trace(f'raster bounds (geo coordinates): {raster_bounds}')

        red = fin.read(3)
        green = fin.read(2)
        blue = fin.read(1)
        logger.trace(f'fin: {fin}')
        logger.trace(f'fin meta: {fin.meta}')
        logger.trace(f'fin crs: {fin.crs}')
        # Получаем трансформацию
        transform = fin.transform
        logger.trace(f'fin transform: {transform}')
        # Пример: получение географических координат для пикселя (x, y)
        x_pixel, y_pixel = 100, 100  # Индексы пикселей
        x_geo, y_geo = transform * (x_pixel, y_pixel)
        logger.trace(f'x_geo, y_geo: {x_geo, y_geo}')
        pixel_size_x, pixel_size_y = fin.res
        logger.trace(f"Pixel size X: {pixel_size_x}, Pixel size Y: {pixel_size_y}")

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
    crs: int = 4326
    # Чтение GeoJSON файла
    gdf = gpd.read_file(geojson_path)
    # gdf = gdf.to_crs(4326)
    gdf.tags.unique()
    # Проверка CRS и установка, если необходимо
    if gdf.crs is None:
        gdf.set_crs(epsg=crs, inplace=True)
        logger.trace(f'GDF CRS IS NONE! Setting to {crs}!')
    else:
        logger.trace(f'GDF CRS is not None!: {gdf.crs}')

    logger.trace("GeoDataFrame total bounds:", gdf.total_bounds)

    # Убедитесь, что у вас есть колонка с геометрией
    if 'geometry' not in gdf.columns:
        raise ValueError("GeoDataFrame does not contain a 'geometry' column.")
    else:
        logger.trace(f"GeoDataFrame contains a 'geometry' column: {gdf['geometry'][0]} and so on...")

    # Установите активную геометрию
    # gdf.set_geometry('geometry', inplace=True)

    # Преобразуем координаты из геоJSON в проекцию, совместимую с TIFF
    # gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom.translate(
    #     xoff=-x_min,
    #     yoff=y_max,
    #     rotation=geom.rotation + 180
    # ))

    # # Определите параметры трансформации
    pixel_size_x = 0.0001459
    pixel_size_y = 0.0000879
    # замените pixel_size_x и pixel_size_y на реальные значения
    _transform = from_origin(58.53,
                             51.22,
                             pixel_size_x,
                             pixel_size_y)

    # Применение трансформации к геометрии
    # def transform_geometry(geom):
    #     if geom.is_empty:
    #         return geom
    #
    #     if isinstance(geom, Point):
    #         return Point(_transform * (geom.x, geom.y))
    #
    #     elif isinstance(geom, Polygon):
    #         # Получаем координаты внешней границы полигона
    #         x, y = geom.exterior.xy
    #         transformed_points = [_transform * (xi, yi) for xi, yi in zip(x, y)]
    #         # Создаем новый полигон из трансформированных точек
    #         return Polygon(transformed_points)
    #
    #     # Добавьте обработку других типов геометрии, если это необходимо
    #     return geom  # Возвращаем оригинальную геометрию, если тип не поддерживается

    # gdf['geometry'] = gdf['geometry'].apply(transform_geometry)

    # # Преобразуйте геометрию в соответствии с трансформацией
    # gdf['geometry'] = gdf['geometry'].apply(lambda geom: transform_geom(_transform, geom))

    # Преобразуйте геометрию в соответствии с трансформацией
    # gdf['geometry'] = gdf['geometry'].apply(lambda geom: transform_geom('EPSG:4326', 'EPSG:3857', geom))

    # Сравнение границ
    logger.trace("GeoDataFrame total bounds after convert:", gdf.total_bounds)

    # Создание фигуры и осей
    fig, ax = plt.subplots(figsize=(12, 12))

    # Отображение растрового изображения
    # ax.imshow(img, extent=[-180, 180, -90, 90])  # Замените на ваши реальные координаты
    with rasterio.open(IMG_FILE) as dataset:
        plt.show(dataset.read(10), transform=dataset.transform, ax=ax, cmap='viridis')
        gdf.plot(ax=ax, color='red')

    # Отображение векторных данных
    gdf.plot(ax=ax, edgecolor='red', linewidth=2)  # Красные контуры для векторных данных

    # logger.trace(f'gdf head: {gdf.head()}')

    # Настройка графика
    ax.set_title('Raster and GeoJSON Overlay')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()


def smth2(img, osm):
    """ TODO """

    logger.info(f'Running smth2...')

    tiff_transform_data: Affine | None = None
    tiff_width: int = 0
    tiff_height: int = 0

    with rasterio.open(img) as tif:
        logger.debug(f'IMG INFO:')
        raster_bounds = tif.bounds
        logger.trace(f'raster bounds (geo coordinates): {raster_bounds}')

        # red = tif.read(3)
        # green = tif.read(2)
        # blue = tif.read(1)
        # logger.trace(f'tif: {tif}') # <open DatasetReader name='S:/xakaton/.../9_1.tif' mode='r'>
        # logger.trace(f'tif meta crs: {tif.meta["crs"]}')
        # logger.trace(f'tif meta transform: {tif.meta["transform"]}')

        logger.trace(f'tif meta: {tif.meta}')
        logger.debug(f'tif crs: {tif.crs}')

        tiff_transform_data = tif.transform  # Получаем трансформацию
        tiff_width, tiff_height = tif.width, tif.height
        # logger.warning(f'type of transform: {type(transform)}')
        logger.debug(f'tiff_transform_data: \n{tiff_transform_data}')
        logger.debug(f'tiff width and height: {tiff_width}, {tiff_height}')
        logger.trace(f'tif transform column vectors: {tif.transform.column_vectors}')
        logger.trace(f'tif transform identity: {tif.transform.identity()}')

        # Пример: получение географических координат для пикселя (x, y)
        logger.trace(f'x0_geo, y0_geo: {tiff_transform_data * (0, 0)}')

        pixel_size_x, pixel_size_y = tif.res
        logger.trace(f"Pixel size X: {pixel_size_x}, Pixel size Y: {pixel_size_y}")

    data = gpd.read_file(GJ_FILE)
    data = data.to_crs(epsg=4326)  # does nothing because img is also 4326
    # length is 5313 rows. Columns:
    # type - (object) way
    # id - (int32) number like 971339425 or 94117797
    # tags - (object) house, detached, ruins (type of object (house?))
    # geometry - geometry

    logger.trace(f'data head: {data.head()}')
    logger.trace(f'data tags unique: {data.tags.unique()}')
    # print_geo_data_frame(gdf=data)

    logger.warning(f'Executing affine transform...')

    #  [a, b, d, e, xoff, yoff]
    # tr_matrix: list =
    # f_stroke: object = data.iloc[[0]]
    f_stroke: GeoDataFrame = data.head(1)
    logger.info(f'f_stroke: {f_stroke}')

    shapely_version_tiff_tr_data = tiff_transform_data.to_shapely()
    logger.trace(f'shapely_version_tiff_tr_data: \n{shapely_version_tiff_tr_data}')
    transformed_data: GeoDataFrame = data.affine_transform(shapely_version_tiff_tr_data)
    logger.info(f'Transformed data!')

    f_stroke = transformed_data.head(1)
    logger.info(f'f_stroke after transformation: {f_stroke}')

    logger.trace(f'transformed data head: {transformed_data.head()}')
    # logger.trace(f'transformed data tags unique: {transformed_data.tags.unique()}')
    # print_geo_data_frame(gdf=transformed_data)

    # for _, row in data.iterrows():
    #     logger.trace(f'row: {row}')

    # data.explore()

    # fig, ax = plt.subplots(1, figsize=(12, 12))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 12))

    with rasterio.open(IMG_FILE) as dataset:
        logger.debug(f'Plotting raster image...')
        a = show(dataset.read(10), transform=dataset.transform, ax=ax1, cmap='viridis')
        data.plot(ax=ax1, color='red')
        ax1.set_title('Первый график')

    with rasterio.open(IMG_FILE) as dataset:
        logger.debug(f'Plotting raster image on the second subplot...')
        show(dataset.read(10), transform=dataset.transform, ax=ax2, cmap='viridis')
        transformed_data.plot(ax=ax2, color='red')
        ax2.set_title('Второй график')

    plt.show()


def print_geo_data_frame(gdf: GeoDataFrame) -> None:
    logger.trace(f'data head: {gdf.head()}')
    logger.trace(f'data type: {gdf["type"]}')
    logger.trace(f'data id: {gdf["id"]}')
    logger.trace(f'data tags: {gdf["tags"]}')
    logger.trace(f'data geometry: {gdf["geometry"]}')


if __name__ == '__main__':
    logger_set_up()
    # plot_data(IMG_FILE, GJ_FILE)
    smth2(IMG_FILE, GJ_FILE)
    # plot_data2(IMG_FILE, GJ_FILE)
    # logger.trace(type(IMG2_FILE))
