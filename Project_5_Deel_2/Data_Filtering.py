import pandas as pd

import numpy as np
 
# Updated bus dimensions (meters)

bus_width = 2.55  # Width of the bus (frontal face)

bus_length = 18.15  # Length of the bus (side face)

bus_height = 3.29  # Height of the bus
 
# Updated corners representing the bus in 2D (width x length)

bus_corners = np.array([

    [-bus_width / 2, -bus_length / 2],  # Bottom-left corner

    [bus_width / 2, -bus_length / 2],   # Bottom-right corner

    [-bus_width / 2, bus_length / 2],   # Top-left corner

    [bus_width / 2, bus_length / 2]     # Top-right corner

])
 
# Function to rotate the bus corners and calculate the effective surface area

def calculate_effective_surface_2D(data):

    effective_surface_areas = []

    for wind_angle in data['Wind_direction_to_bus_radians']:

        # Create rotation matrix for the given wind angle

        rotation_matrix = np.array([

            [np.cos(wind_angle), -np.sin(wind_angle)],

            [np.sin(wind_angle),  np.cos(wind_angle)]

        ])

        # Rotate the bus corners

        rotated_corners = bus_corners @ rotation_matrix.T

        # Effective width (x-dimension projection)

        effective_width = rotated_corners[:, 0].max() - rotated_corners[:, 0].min()

        # Effective surface area (width * height)

        effective_surface_area = effective_width * bus_height

        effective_surface_areas.append(effective_surface_area)

    return effective_surface_areas
 
# Additional functions from the original code

def acceleration(data):

    data['Acceleration'] = data['WheelBasedVehicleSpeed'].diff() / 1  # Delta t = 1 second

    data.loc[0, 'Acceleration'] = 0  # Set the first value to 0

    return data
 
def no_brakes(data):

    data = data[data['BrakePedalPos'] == 0]

    return data
 
def P_in(data):

    data['P_in'] = data['DICO3_DCLinkVoltageDriveSystem'] * data['DICO3_DCLINKTractionCurrent']

    return data
 
def P_dissipation(data):

    data['P_dissipation'] = data['P_in'] - data['P_out']

    return data
 
def efficiency(data):

    data['Efficiency'] = np.where(data['P_in'] != 0, data['P_out'] / data['P_in'], np.nan)

    return data
 
def omega_calculation(data):

    data['omega'] = (2 * np.pi * data['n']) / 60

    return data
 
def torque_calculation(data):

    data['Torque'] = np.where(data['omega'] != 0, data['P_out'] / data['omega'], 0)

    return data
 
def max_weight(data):

    data['max_loaded_weight'] = 29000

    return data
 
def min_weight(data):

    data['min_weight'] = 19150

    return data
 
def total_weight(data):

    data['total_weight'] = data['Payload'] + data['min_weight']

    return data
 
def wind_speed_bus(data):

    data[['Wind_direction_to_earth_radians', 'Wind_direction_to_bus_radians']] = np.radians(data[['Wind_direction_to_earth', 'Wind_direction_to_bus']])

    data['Wind_speed_m/s'] = data['Wind_speed'] / 3.6

    data['effective_wind_speed_m/s'] = np.cos(data['Wind_direction_to_bus_radians']) * data['Wind_speed_m/s']

    return data
 
def delta_wind_speed(data):

    data['delta_wind_speed_m/s'] = data['WheelBasedVehicleSpeed'] - data['effective_wind_speed_m/s']

    return data
 
def average_eff_wind_speed(data):

    data['average_effective_wind_speed_m/s'] = data['effective_wind_speed_m/s'].mean()

    return data
 
def clean_data(data):

    data = data.replace([np.inf, -np.inf], np.nan)

    data = data.fillna('')  # Replace NaN with an empty string

    return data
 
def main():

    # Read the Excel file into a DataFrame

    df = pd.read_excel('data_project_05.xlsx')

    df_filtered = df.copy()

    # Apply transformations

    df_filtered = acceleration(df_filtered)

    df_filtered = no_brakes(df_filtered)

    df_filtered = max_weight(df_filtered)

    df_filtered = min_weight(df_filtered)

    df_filtered = total_weight(df_filtered)

    df_filtered = wind_speed_bus(df_filtered)

    df_filtered = delta_wind_speed(df_filtered)

    df_filtered = average_eff_wind_speed(df_filtered)

    df_filtered = P_in(df_filtered)

    df_filtered = P_dissipation(df_filtered)

    df_filtered = efficiency(df_filtered)

    df_filtered = omega_calculation(df_filtered)

    df_filtered = torque_calculation(df_filtered)

    df_filtered['Effective_Surface_Area_m2'] = calculate_effective_surface_2D(df_filtered)

    df_filtered['Average_Effective_Surface_Area_m2'] = df_filtered['Effective_Surface_Area_m2'].mean()

    # Clean data before saving

    df_filtered = clean_data(df_filtered)

    # Save the filtered DataFrame to an Excel file

    df_filtered.to_excel('filtered_data.xlsx', index=False, engine='openpyxl')

    print('File saved')
 
if __name__ == '__main__':

    main()

 