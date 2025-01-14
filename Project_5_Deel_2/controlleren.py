import numpy as np
import pandas as pd
import rasterio
from scipy.interpolate import RegularGridInterpolator
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# Stap 1: Laad de rasterdata
with rasterio.open('QgisMerge.tif') as src: # Opent het tiff bestand
    raster_data = src.read(1)  # Lees de eerste band, deze bevat de hoogte data
    bounds = src.bounds # Krijg de grenzen van het cooordinatensysteem
    resolution = src.res  # Afmetingen van de pixels in meter 
    width, height = src.width, src.height # breette en hoogte van het aantal rasters
    # Dit doe je om te bepalen welke GPS-coördinaten overeenkomen met specifieke pixels in het raster.

# Forceer raster CRS naar RD New (EPSG:28992)
raster_crs = "EPSG:28992" # Zodat de coordinaten van de busdata overeenkomen met de coordinaten van de rasterdata

# Maak X- en Y-coördinaten voor het raster
x = np.linspace(bounds.left, bounds.right, width)  # Longitude (X)
y = np.linspace(bounds.top, bounds.bottom, height)  # Latitude (Y)
raster_data = raster_data.astype(float)

# Stap 2: Laad de GPS-data
gps_data = pd.read_excel('data_project_05.xlsx', sheet_name='sheet_01')
gps_longitude = gps_data['gps_1'].values  # Longitude
gps_latitude = gps_data['gps_0'].values  # Latitude

# Stap 3: Converteer GPS-coördinaten naar RD New
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
gps_x, gps_y = transformer.transform(gps_longitude, gps_latitude)

# Stap 4: Interpolatie - Koppel GPS-punten aan hoogtewaarden
interpolator = RegularGridInterpolator((y[::-1], x), raster_data, bounds_error=False, fill_value=np.nan)
gps_points = np.array([gps_y, gps_x]).T
heights = interpolator(gps_points)

# Stap 5: Plot een 3D-lijnweergave
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Kleuren instellen op basis van hoogte
norm = Normalize(vmin=np.nanmin(heights), vmax=np.nanmax(heights))
colors = plt.cm.viridis(norm(heights))

# Plot de lijn in 3D
for i in range(len(gps_x) - 1):
    ax.plot(
        gps_x[i:i + 2], gps_y[i:i + 2], heights[i:i + 2],
        color=colors[i],
        linewidth=2
    )

# Kleurenbalk toevoegen
sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.1)
cbar.set_label('Hoogte boven NAP (m)', fontsize=12)

# Labels en titel
ax.set_title('Hoogte boven NAP langs de route', fontsize=16)
ax.set_xlabel('Longitude (m)', fontsize=12)
ax.set_ylabel('Latitude (m)', fontsize=12)
ax.set_zlabel('Hoogte (m)', fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=10)

# Weergave optimaliseren
plt.tight_layout()
plt.show()

