import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from pyproj import Transformer

# Function to remove outliers
def remove_outliers(data, threshold=30):
    data = np.array(data)  # Ensure it is a NumPy array
    data[data > threshold] = np.nan  # Remove outliers above the threshold
    return data

# Function to calculate slope
def calculate_slope(heights, distances):
    slopes = np.zeros(len(heights))  # Initialize an array for the slopes
    for i in range(1, len(heights)):
        delta_height = heights[i] - heights[i - 1]  # Difference in elevation
        delta_distance = distances[i] - distances[i - 1]  # Difference in distance
        slopes[i] = delta_height / delta_distance if delta_distance != 0 else 0  # Avoid division by zero
    slopes[0] = 0  # Ensure the first slope starts at 0
    return slopes

# Function to convert slope to degrees
def slope_to_degrees(slopes):
    return np.arctan(slopes) * (180 / np.pi)

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
raster_data = np.nan_to_num(raster_data.astype(float), nan=0.0)  # Fix NaN values

# Step 2: Load the GPS data of the bus route
gps_data = pd.read_excel('data_project_05.xlsx', sheet_name='sheet_01')
gps_longitude = gps_data['gps_1'].values  # Longitude
gps_latitude = gps_data['gps_0'].values  # Latitude

# Convert GPS coordinates to RD New (EPSG:28992)
raster_crs = "EPSG:28992"
transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
gps_x, gps_y = transformer.transform(gps_longitude, gps_latitude)

# Step 3: Interpolate the elevations along the bus route
route_coords = np.array(list(zip(gps_x, gps_y)))  # Combine x and y coordinates

with rasterio.open('QgisMerge.tif') as src:
    route_heights = np.array([val[0] for val in src.sample(route_coords)])  # Retrieve elevations

# Step 4: Remove outliers
filtered_heights = remove_outliers(route_heights, threshold=30)

# Fill NaN values with linear interpolation
valid_indices = ~np.isnan(filtered_heights)
interp_func = np.interp(np.arange(len(filtered_heights)), np.arange(len(filtered_heights))[valid_indices], filtered_heights[valid_indices])
filtered_heights = interp_func

# Step 5: Apply a Gaussian filter to smooth the data
smoothed_heights = gaussian_filter1d(filtered_heights, sigma=150)  # Sigma determines the degree of smoothing

# Step 6: Calculate cumulative distance along the route
gps_data['distance'] = np.sqrt(
    (gps_data['gps_1'].diff() * 111320) ** 2 +  # Convert longitude to meters
    (gps_data['gps_0'].diff() * 110540) ** 2   # Convert latitude to meters
).fillna(0).cumsum()  # Cumulative distance

# Step 7: Calculate the slope at each point
gps_data['slope'] = calculate_slope(smoothed_heights, gps_data['distance'])

# Step 8: Convert slope to degrees
gps_data['slope_degrees'] = slope_to_degrees(gps_data['slope'])

# Add the smoothed elevations to the original GPS data
gps_data['smoothed_heights'] = smoothed_heights  # Add the smoothed elevations as a new column

# Step 9: Save to Excel
output_file = 'degree.xlsx'
gps_data.to_excel(output_file, index=False)

print(f"File with smoothed elevations, slopes, and degrees saved as: {output_file}")

# Plot the original and smoothed elevations with clearer color contrast
plt.figure(figsize=(12, 6))
plt.plot(gps_data['distance'], route_heights, label='Original elevations', linestyle='dotted', color='darkblue', alpha=1, linewidth=2)
plt.plot(gps_data['distance'], smoothed_heights, label='Smoothed elevations (Gaussian)', color='red', linewidth=2)
plt.title('Elevations along the Bus Route', fontsize=16)
plt.xlabel('Distance along the route (m)', fontsize=12)
plt.ylabel('Elevation (m)', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

