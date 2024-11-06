import pandas as pd

# lees data
omloopplanning = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")


def Twee_dataframes(dienstregeling, afstandsmatrix):
    # Convert 'vertrektijd' column to datetime, with error handling
    dienstregeling['vertrektijd'] = pd.to_datetime(dienstregeling['vertrektijd'], format='%H:%M', errors='coerce')
    # Drop rows where 'vertrektijd' could not be converted
    dienstregeling = dienstregeling.dropna(subset=['vertrektijd'])

    # Merge dienstregeling with afstandsmatrix on 'startlocatie', 'eindlocatie', and 'buslijn' to get max reistijd in min
    dienstregeling = dienstregeling.merge(
        afstandsmatrix[['startlocatie', 'eindlocatie', 'max reistijd in min', 'buslijn']], 
        on=['startlocatie', 'eindlocatie', 'buslijn'], 
        how='left'
    )

    # Calculate 'eindtijd' by adding 'max reistijd in min' to 'vertrektijd'
    dienstregeling['eindtijd'] = dienstregeling['vertrektijd'] + pd.to_timedelta(dienstregeling['max reistijd in min'], unit='m')

    # Separate the DataFrame for routes from 'ehvapt' to 'ehvbst'
    Begin_airport = dienstregeling[(dienstregeling['startlocatie'] == 'ehvapt') & (dienstregeling['eindlocatie'] == 'ehvbst')]
    Begin_airport['early_morning'] = Begin_airport['vertrektijd'].dt.hour < 5
    Begin_airport = Begin_airport.sort_values(by=['early_morning', 'vertrektijd']).reset_index(drop=True)
    Begin_airport = Begin_airport.drop(columns=['early_morning'])

    # Separate the DataFrame for routes from 'ehvbst' to 'ehvapt'
    Begin_station = dienstregeling[(dienstregeling['startlocatie'] == 'ehvbst') & (dienstregeling['eindlocatie'] == 'ehvapt')]
    Begin_station['early_morning'] = Begin_station['vertrektijd'].dt.hour < 5
    Begin_station = Begin_station.sort_values(by=['early_morning', 'vertrektijd']).reset_index(drop=True)
    Begin_station = Begin_station.drop(columns=['early_morning'])

    return Begin_station, Begin_airport

Begin_station, Begin_airport = Twee_dataframes(dienstregeling, afstandsmatrix)


