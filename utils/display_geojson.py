"""
Файлик-playground для гео-джейсонов
pip install geojson
pip install matplotlib (for plot)
"""

import geopandas as gpd
import matplotlib.pyplot as plt

from user_settings import geojson_file_path

gdf = gpd.read_file(geojson_file_path)  # load data

# print(gdf.head())
# print(type(gdf))
gdf.plot()
plt.show()
