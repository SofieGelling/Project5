import pandas as pd
import numpy as np

def no_brakes(data):
    # Filter data where BrakePedalPos is 0
    data = data[data['BrakePedalPos'] == 0]
    return data

def P_in(data):
    # Add P engine in column
    data['P_in'] = data['DICO3_DCLinkVoltageDriveSystem']*data['DICO3_DCLINKTractionCurrent']
    return data

def P_dissipation(data):
    # Add P engine dissipation column
    data['P_dissipation'] = data['P_in'] - data['P_out']
    return data

def max_weight(data):
    # Add max loaded weight column
    data['max_loaded_weight'] = 29000
    return data

def min_weight(data):
    # Add min empty weight column
    data['min_weight'] = 19150
    return data

def total_weight(data):
    # Calculate total weight as Payload + min_weight
    data['total_weight'] = data['Payload'] + data['min_weight']
    return data

def wind_speed_bus(data):
    # Convert wind directions to radians and calculate effective wind speed
    data[['Wind_direction_to_earth_radians', 'Wind_direction_to_bus_radians']] = np.radians(data[['Wind_direction_to_earth', 'Wind_direction_to_bus']])
    data['Wind_speed_m/s'] = data['Wind_speed']/3.6
    data['effective_wind_speed_m/s'] = np.cos(data['Wind_direction_to_bus_radians']) * data['Wind_speed_m/s']
    return data

def delta_wind_speed(data):
    # Calculate delta wind speed
    data['delta_wind_speed_m/s'] = data['WheelBasedVehicleSpeed'] - data['effective_wind_speed_m/s']
    return data

def average_eff_wind_speed(data):
    # Add the mean of effective wind speed to all rows
    data['average_effective_wind_speed_m/s'] = data['effective_wind_speed_m/s'].mean()
    return data

def main():

    # Read the Excel file into a DataFrame
    df = pd.read_excel('data_project_05.xlsx')
    df_filtered = df.copy()

    # Apply transformations
    df_filtered = no_brakes(df_filtered)
    df_filtered = max_weight(df_filtered)
    df_filtered = min_weight(df_filtered)
    df_filtered = total_weight(df_filtered)
    df_filtered = wind_speed_bus(df_filtered)
    df_filtered = delta_wind_speed(df_filtered)
    df_filtered = average_eff_wind_speed(df_filtered)
    df_filtered = P_in(df_filtered)
    df_filtered = P_dissipation(df_filtered)

    # Save the filtered DataFrame to an Excel file
    df_filtered.to_excel('filtered_data_project_5_deel_2.xlsx', index=False)

if __name__ == '__main__':
    main()
