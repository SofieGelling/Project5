import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import gaussian_filter1d
from pyproj import Transformer

# Functie om uitschieters te verwijderen
def remove_outliers(data, threshold=30):
    data = np.array(data)  # Zorg ervoor dat het een NumPy-array is
    data[data > threshold] = np.nan  # Verwijder uitschieters boven de drempel
    return data

# Stap 1: Laad de rasterdata (hoogtekaart)
with rasterio.open('QgisMerge.tif') as src:
    raster_data = src.read(1)  # Hoogtedata
    bounds = src.bounds
    resolution = src.res
    width, height = src.width, src.height
    transform = src.transform

# Maak X- en Y-coördinaten voor de rasterdata
x = np.linspace(bounds.left, bounds.right, width)  # X-coördinaten
y = np.linspace(bounds.top, bounds.bottom, height)  # Y-coördinaten
raster_data = np.nan_to_num(raster_data.astype(float), nan=0.0)  # Repareer NaN-waarden

# Stap 2: Laad de GPS-data van de busroute
gps_data = pd.read_excel('data_project_05.xlsx', sheet_name='sheet_01')
gps_longitude = gps_data['gps_1'].values  # Longitude
gps_latitude = gps_data['gps_0'].values  # Latitude

# Converteer GPS-coördinaten naar RD New (EPSG:28992)
raster_crs = "EPSG:28992"
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
gps_x, gps_y = transformer.transform(gps_longitude, gps_latitude)

# Stap 3: Interpoleer de hoogtes langs de busroute
route_coords = np.array(list(zip(gps_x, gps_y)))  # Combineer x- en y-coördinaten

with rasterio.open('QgisMerge.tif') as src:
    route_heights = np.array([val[0] for val in src.sample(route_coords)])  # Haal hoogtes op

# Stap 4: Verwijder uitschieters
filtered_heights = remove_outliers(route_heights, threshold=30)

# Vul NaN-waarden op met lineaire interpolatie
valid_indices = ~np.isnan(filtered_heights)
interp_func = np.interp(np.arange(len(filtered_heights)), np.arange(len(filtered_heights))[valid_indices], filtered_heights[valid_indices])
filtered_heights = interp_func

# Stap 5: Pas een Gaussisch filter toe om de data te smoothen
smoothed_heights = gaussian_filter1d(filtered_heights, sigma=30)  # Sigma bepaalt de mate van smoothing

# Voeg de gesmoothe hoogtes toe aan de originele GPS-data
gps_data['smoothed_heights'] = smoothed_heights  # Voeg de gesmoothe hoogtes als nieuwe kolom toe

# Opslaan in een nieuwe Excel-file
output_file = 'gps_data_with_smoothed_heights.xlsx'
gps_data.to_excel(output_file, index=False)

print(f"Bestand opgeslagen als: {output_file}")

