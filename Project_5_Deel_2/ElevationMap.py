import numpy as np
import pandas as pd
import rasterio
from scipy.interpolate import RegularGridInterpolator
from pyproj import Transformer
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# Step 1: Load the raster data
with rasterio.open('QgisMerge.tif') as src:  # Opens the TIFF file
    raster_data = src.read(1)  # Reads the first band, which contains the elevation data
    bounds = src.bounds  # Get the boundaries of the coordinate system
    resolution = src.res  # Dimensions of the pixels in meters
    width, height = src.width, src.height  # Width and height of the number of raster cells
    # This is done to determine which GPS coordinates correspond to specific pixels in the raster.

# Force raster CRS to RD New (EPSG:28992)
raster_crs = "EPSG:28992"  # Ensures that the coordinates of the bus data match the coordinates of the raster data

# Create X and Y coordinates for the raster
x = np.linspace(bounds.left, bounds.right, width)  # Longitude (X)
y = np.linspace(bounds.top, bounds.bottom, height)  # Latitude (Y)
raster_data = raster_data.astype(float)

# Step 2: Load the GPS data
gps_data = pd.read_excel('data_project_05.xlsx', sheet_name='sheet_01')
gps_longitude = gps_data['gps_1'].values  # Longitude
gps_latitude = gps_data['gps_0'].values  # Latitude

# Step 3: Convert GPS coordinates to RD New
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
gps_x, gps_y = transformer.transform(gps_longitude, gps_latitude)

# Step 4: Interpolation - Link GPS points to elevation values
interpolator = RegularGridInterpolator((y[::-1], x), raster_data, bounds_error=False, fill_value=np.nan)
gps_points = np.array([gps_y, gps_x]).T
heights = interpolator(gps_points)

# Addition: Transform RD New coordinates (meters) back to EPSG:4326 (degrees)
reverse_transformer = Transformer.from_crs(raster_crs, "EPSG:4326", always_xy=True)
gps_longitude_degrees, gps_latitude_degrees = reverse_transformer.transform(gps_x, gps_y)

# Step 5: Plot a 3D line representation
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Set colors based on elevation
norm = Normalize(vmin=np.nanmin(heights), vmax=np.nanmax(heights))
colors = plt.cm.viridis(norm(heights))

# Plot the line in 3D with coordinates in degrees
for i in range(len(gps_longitude_degrees) - 1):
    ax.plot(
        gps_longitude_degrees[i:i + 2], gps_latitude_degrees[i:i + 2], heights[i:i + 2],
        color=colors[i],
        linewidth=1
    )

# Add a color bar
sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.1)
cbar.set_label('Elevation above NAP (m)', fontsize=12)

# Labels and title
ax.set_title('Elevation above NAP along the route', fontsize=16)
ax.set_xlabel('Longitude (degrees)', fontsize=12)
ax.set_ylabel('Latitude (degrees)', fontsize=12)
ax.set_zlabel('Elevation (m)', fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=10)

# Optimize display
plt.tight_layout()
plt.show()

