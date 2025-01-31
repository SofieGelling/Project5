import pandas as pd

import matplotlib.pyplot as plt

import numpy as np
 
def filter_efficiency(data):

    """

    Filters invalid efficiency data:

    - Removes rows where P_in <= 0 or P_out < 0

    - Clamps efficiency values to the range [0, 1]

    """

    data = data[(data['P_in'] > 0) & (data['P_out'] >= 0)]

    data.loc[:, 'Efficiency'] = np.clip(data['Efficiency'], 0, 1)

    return data
 
def main():

    # Load the provided data

    file_path = 'filtered_data.xlsx'

    df = pd.read_excel(file_path)
 
    # Ensure required columns are present

    required_columns = ['n', 'Torque', 'Efficiency', 'P_in', 'P_out']

    if not all(col in df.columns for col in required_columns):

        missing_cols = [col for col in required_columns if col not in df.columns]

        raise ValueError(f"Missing columns in the dataset: {missing_cols}")
 
    # Filter and clean the data

    df = filter_efficiency(df)
 
    # **Filter out negative Torque values**

    df = df[df['Torque'] >= 0]
 
    # Define bin sizes for Torque and RPM

    torque_bins = np.linspace(df['Torque'].min(), df['Torque'].max(), 50)

    rpm_bins = np.linspace(df['n'].min(), df['n'].max(), 50)
 
    # Add binned columns to the DataFrame

    df['Torque_binned'] = pd.cut(df['Torque'], bins=torque_bins, labels=torque_bins[:-1])

    df['n_binned'] = pd.cut(df['n'], bins=rpm_bins, labels=rpm_bins[:-1])
 
    # Filter valid data for Efficiency, Torque, and n

    df = df.dropna(subset=['Efficiency', 'Torque_binned', 'n_binned'])
 
    # Create a pivot table for the efficiency map

    pivot_table = df.pivot_table(

        index='Torque_binned',

        columns='n_binned',

        values='Efficiency',

        aggfunc='mean',

        observed=False

    )
 
    # Plot the efficiency map with a rainbow colormap

    plt.figure(figsize=(10, 8))

    contour = plt.contourf(

        pivot_table.columns.astype(float),

        pivot_table.index.astype(float),

        pivot_table.values,

        cmap='rainbow',

        levels=20

    )
 
    plt.colorbar(contour, label='Efficiency (%)')

    plt.title('Efficiency Map (n, Torque, η)')

    plt.xlabel('Speed (RPM)')

    plt.ylabel('Torque (Nm)')

    plt.grid()

    plt.show()
 
if __name__ == '__main__':

    main()

 