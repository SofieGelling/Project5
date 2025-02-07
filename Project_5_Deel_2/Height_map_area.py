import numpy as np
import pandas as pd
import rasterio
from scipy.interpolate import RegularGridInterpolator
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, Normalize
from matplotlib import cm
from matplotlib.colorbar import ColorbarBase

# Step 1: Load the raster data (elevation map)
with rasterio.open('QgisMerge.tif') as src:
    raster_data = src.read(1)  # Elevation data
    bounds = src.bounds
    resolution = src.res
    width, height = src.width, src.height
    transform = src.transform

# Create X and Y coordinates for the raster data
x = np.linspace(bounds.left, bounds.right, width)  # X coordinates
y = np.linspace(bounds.top, bounds.bottom, height)  # Y coordinates
raster_data = raster_data.astype(float)

# Step 2: Load the GPS data of the bus route
gps_data = pd.read_excel('data_project_05.xlsx', sheet_name='sheet_01')
gps_longitude = gps_data['gps_1'].values  # Longitude
gps_latitude = gps_data['gps_0'].values  # Latitude

# Convert GPS coordinates to RD New (EPSG:28992)
raster_crs = "EPSG:28992"
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
gps_x, gps_y = transformer.transform(gps_longitude, gps_latitude)

# Step 3: Determine the buffer (e.g., 500 meters around the route)
buffer_distance = 500  # Buffer in meters
min_x, max_x = gps_x.min() - buffer_distance, gps_x.max() + buffer_distance
min_y, max_y = gps_y.min() - buffer_distance, gps_y.max() + buffer_distance

# Crop the raster data within the buffer
x_indices = np.where((x >= min_x) & (x <= max_x))[0]
y_indices = np.where((y >= min_y) & (y <= max_y))[0]
buffered_raster = raster_data[y_indices.min():y_indices.max() + 1, x_indices.min():x_indices.max() + 1]
buffered_x = x[x_indices]
buffered_y = y[y_indices]

# Step 4: Visualize the environment as a relief map
fig, ax = plt.subplots(figsize=(12, 8))
ls = LightSource(azdeg=315, altdeg=45)  # Light source for shading
cmap = cm.get_cmap('terrain')  # Ensure clear color distinctions
norm = Normalize(vmin=buffered_raster.min(), vmax=buffered_raster.max())  # Normalize elevation values

# Create a shaded relief representation of the elevation data
shaded_relief = ls.shade(buffered_raster, cmap=cmap, blend_mode='overlay', vert_exag=1)

# Display the relief map
extent = [buffered_x[0], buffered_x[-1], buffered_y[-1], buffered_y[0]]
im = ax.imshow(shaded_relief, extent=extent, origin='upper')

# Add the bus route as an overlay
ax.plot(gps_x, gps_y, color='red', linewidth=2, label='Bus route')

# Add a color scale
cbar_ax = fig.add_axes([0.92, 0.25, 0.02, 0.5])  # Location of the color scale
ColorbarBase(cbar_ax, cmap=cmap, norm=norm, orientation='vertical', label='Elevation (m)')

# Labels and legend
ax.set_title('Relief map of the environment with bus route', fontsize=16)
ax.set_xlabel('X coordinates (m)', fontsize=12)
ax.set_ylabel('Y coordinates (m)', fontsize=12)
ax.legend(fontsize=12)

plt.tight_layout(rect=[0, 0, 0.9, 1])  # Leave space for the color scale
plt.show()
