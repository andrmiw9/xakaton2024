"""
Файлик-playground для гео-джейсонов
pip install geojson
pip install matplotlib (for plot)
"""

import geopandas as gpd
import matplotlib.pyplot as plt

from user_settings import GJ_FILE

gdf = gpd.read_file(GJ_FILE)  # load data

# print(gdf.head())
# print(type(gdf))
gdf.plot()
plt.show()
