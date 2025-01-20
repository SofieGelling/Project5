import numpy as np
import pandas as pd
import rasterio
from scipy.interpolate import RegularGridInterpolator
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, Normalize
from matplotlib import cm
from matplotlib.colorbar import ColorbarBase

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
raster_data = raster_data.astype(float)

# Stap 2: Laad de GPS-data van de busroute
gps_data = pd.read_excel('data_project_05.xlsx', sheet_name='sheet_01')
gps_longitude = gps_data['gps_1'].values  # Longitude
gps_latitude = gps_data['gps_0'].values  # Latitude

# Converteer GPS-coördinaten naar RD New (EPSG:28992)
raster_crs = "EPSG:28992"
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
gps_x, gps_y = transformer.transform(gps_longitude, gps_latitude)

# Stap 3: Bepaal de buffer (bijvoorbeeld 500 meter rondom de route)
buffer_distance = 500  # Buffer in meters
min_x, max_x = gps_x.min() - buffer_distance, gps_x.max() + buffer_distance
min_y, max_y = gps_y.min() - buffer_distance, gps_y.max() + buffer_distance

# Snijd de rasterdata binnen de buffer
x_indices = np.where((x >= min_x) & (x <= max_x))[0]
y_indices = np.where((y >= min_y) & (y <= max_y))[0]
buffered_raster = raster_data[y_indices.min():y_indices.max() + 1, x_indices.min():x_indices.max() + 1]
buffered_x = x[x_indices]
buffered_y = y[y_indices]

# Stap 4: Visualiseer de omgeving als een reliëfkaart
fig, ax = plt.subplots(figsize=(12, 8))
ls = LightSource(azdeg=315, altdeg=45)  # Lichtbron voor schaduw
cmap = cm.get_cmap('terrain')  # Zorg voor duidelijk onderscheid in kleuren
norm = Normalize(vmin=buffered_raster.min(), vmax=buffered_raster.max())  # Normaliseer hoogtes

# Maak een schaduwrijke weergave van de hoogtedata
shaded_relief = ls.shade(buffered_raster, cmap=cmap, blend_mode='overlay', vert_exag=1)

# Toon de reliëfkaart
extent = [buffered_x[0], buffered_x[-1], buffered_y[-1], buffered_y[0]]
im = ax.imshow(shaded_relief, extent=extent, origin='upper')

# Voeg de busroute toe als overlay
ax.plot(gps_x, gps_y, color='red', linewidth=2, label='Busroute')

# Voeg een kleurenschaal toe
cbar_ax = fig.add_axes([0.92, 0.25, 0.02, 0.5])  # Locatie van de kleurenschaal
ColorbarBase(cbar_ax, cmap=cmap, norm=norm, orientation='vertical', label='Hoogte (m)')

# Labels en legenda
ax.set_title('Reliëfkaart van de omgeving met busroute', fontsize=16)
ax.set_xlabel('X-coördinaten (m)', fontsize=12)
ax.set_ylabel('Y-coördinaten (m)', fontsize=12)
ax.legend(fontsize=12)

plt.tight_layout(rect=[0, 0, 0.9, 1])  # Ruimte vrijhouden voor de kleurenschaal
plt.show()

