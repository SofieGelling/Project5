# Herlaad alle benodigde bibliotheken en data na reset
import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from pyproj import Transformer

# Functie om uitschieters te verwijderen
def remove_outliers(data, threshold=30):
    data = np.array(data)  # Zorg ervoor dat het een NumPy-array is
    data[data > threshold] = np.nan  # Verwijder uitschieters boven de drempel
    return data

# Functie om de helling (slope) te berekenen
def calculate_slope(heights, distances):
    slopes = np.zeros(len(heights))  # Initialiseer een array voor de slopes
    for i in range(1, len(heights)):
        delta_height = heights[i] - heights[i - 1]  # Verschil in hoogte
        delta_distance = distances[i] - distances[i - 1]  # Verschil in afstand
        slopes[i] = delta_height / delta_distance if delta_distance != 0 else 0  # Vermijd deling door nul
    slopes[0] = 0  # Zorg dat de eerste slope begint bij 0
    return slopes

# Functie om slope om te zetten naar graden
def slope_to_degrees(slopes):
    return np.arctan(slopes) * (180 / np.pi)

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
smoothed_heights = gaussian_filter1d(filtered_heights, sigma=150)  # Sigma bepaalt de mate van smoothing

# Stap 6: Bereken de cumulatieve afstand langs de route
gps_data['distance'] = np.sqrt(
    (gps_data['gps_1'].diff() * 111320) ** 2 +  # Lengtegraad omgezet naar meters
    (gps_data['gps_0'].diff() * 110540) ** 2   # Breedtegraad omgezet naar meters
).fillna(0).cumsum()  # Cumulatieve afstand

# Stap 7: Bereken de slope (helling) per punt
gps_data['slope'] = calculate_slope(smoothed_heights, gps_data['distance'])

# Stap 8: Zet slope om naar graden
gps_data['slope_degrees'] = slope_to_degrees(gps_data['slope'])

# Plot de originele en gesmoothe hoogtes met duidelijker kleurcontrast
plt.figure(figsize=(12, 6))
plt.plot(gps_data['distance'], route_heights, label='Originele hoogtes', linestyle='dotted', color='darkblue', alpha=1, linewidth=2)
plt.plot(gps_data['distance'], smoothed_heights, label='Gesmoothe hoogtes (Gaussisch)', color='red', linewidth=2)
plt.title('Hoogtes langs de Busroute', fontsize=16)
plt.xlabel('Afstand langs de route (m)', fontsize=12)
plt.ylabel('Hoogte (m)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

