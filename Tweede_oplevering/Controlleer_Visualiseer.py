import pandas as pd
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def voeg_idle_tijden_toe(df):

    """
    Functie om idle-periodes toe te voegen aan de dataset wanneer er een pauze is tussen opeenvolgende ritten.
    
    Parameters:
    df (pd.DataFrame): Dataframe met omloopplanning. Verwacht kolommen 'startlocatie', 'eindlocatie', 'starttijd datum', 'eindtijd datum', 'omloop nummer'.
    
    Returns:
    pd.DataFrame: Dataframe met toegevoegde idle-periodes.
    """
    # Zorg dat 'starttijd datum' en 'eindtijd datum' kolommen in datetime-formaat zijn
    df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
    df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])
    
    # Sorteer de data op omloop nummer en starttijd voor een juiste volgorde van ritten
    df = df.sort_values(by=['omloop nummer', 'starttijd datum']).reset_index(drop=True)
    nieuwe_rijen = []  # Lege lijst om idle rijen op te slaan

    # Loop door elke omloop (buslijn) en controleer de tijdsverschillen tussen ritten
    for omloop_nummer, groep in df.groupby('omloop nummer'):
        for i in range(len(groep) - 1):
            huidige_rit = groep.iloc[i]
            volgende_rit = groep.iloc[i + 1]
            
            # Haal de eindtijd van de huidige rit en starttijd van de volgende rit op
            eindtijd_huidige = huidige_rit['eindtijd datum']
            starttijd_volgende = volgende_rit['starttijd datum']
            
            # Bereken het tijdsverschil in minuten
            tijdsverschil = (starttijd_volgende - eindtijd_huidige).total_seconds() / 60.0
            
            # Controleer of er een pauze is (bijvoorbeeld meer dan 1 minuut verschil)
            if tijdsverschil > 0:
                idle_rij = {
                    'startlocatie': huidige_rit['eindlocatie'],
                    'eindlocatie': huidige_rit['eindlocatie'],
                    'starttijd': eindtijd_huidige.time(),  # Alleen tijd zonder datum
                    'eindtijd': starttijd_volgende.time(),
                    'activiteit': 'idle',
                    'buslijn': None,
                    'energieverbruik': 0.01,  # Energieverbruik tijdens idle
                    'starttijd datum': eindtijd_huidige,
                    'eindtijd datum': starttijd_volgende,
                    'omloop nummer': omloop_nummer
                }
                nieuwe_rijen.append(idle_rij)

    # Voeg de idle-rijen toe aan de originele dataframe en sorteer opnieuw
    df = pd.concat([df, pd.DataFrame(nieuwe_rijen)], ignore_index=True)
    df = df.sort_values(by=['omloop nummer', 'starttijd datum']).reset_index(drop=True)
    
    return df

def Afstand_omloop_toevoegen(omloop_file_path, connexxion_file_path):
    
    """
    Voeg een kolom 'afstand' toe aan omloopplanning_df op basis van gegevens in dienstregeling_df.
    
    Parameters:
    omloopplanning_df (pd.DataFrame): Dataframe met omloopplanning data.
    dienstregeling_df (pd.DataFrame): Dataframe met dienstregeling data.
    
    Returns:
    pd.DataFrame: Dataframe met toegevoegde kolom 'afstand'.
    """
    
    # Read the Excel files
    omloopplanning_data = omloop_file_path
    connexxion_data_distances = connexxion_file_path  # Read distances data from sheet 2

    # Set up a lookup dictionary with both (start, end, buslijn) and (start, end) keys
    distance_lookup = {}
    for _, row in connexxion_data_distances.iterrows():
        key_with_buslijn = (row['startlocatie'], row['eindlocatie'], row.get('buslijn', None))
        key_without_buslijn = (row['startlocatie'], row['eindlocatie'])
        distance_lookup[key_with_buslijn] = row['afstand in meters']
        distance_lookup[key_without_buslijn] = row['afstand in meters']  # For entries without a bus line

    # Define a function to calculate distance using the lookup, handling 'opladen' and 'idle'
    def calculate_distance(row):
        if row['activiteit'] in ['idle', 'opladen']:
            return 0
        # Attempt to find the distance with and without buslijn
        key_with_buslijn = (row['startlocatie'], row['eindlocatie'], row.get('buslijn', None))
        key_without_buslijn = (row['startlocatie'], row['eindlocatie'])
        return distance_lookup.get(key_with_buslijn) or distance_lookup.get(key_without_buslijn) or None

    # Apply the distance calculation to each row
    omloopplanning_data['afstand in meters'] = omloopplanning_data.apply(calculate_distance, axis=1)
    
    return omloopplanning_data

def add_energy_usage_column(df, soh_value=0.85):
    """
    Adds a 'energieverbruik nieuw' column based on specified conditions.
    """
    original_capacity_kWh = 300
    max_charge_percentage = 0.9
    charge_rate_kW = 450
    max_usable_capacity_kWh = original_capacity_kWh * soh_value * max_charge_percentage

    def calculate_energy_usage(row):
        distance_km = (row['afstand in meters'] or 0) / 1000
        if row['activiteit'] == 'idle':
            return 0.01
        elif row['activiteit'] == 'opladen':
            start_time = pd.to_datetime(row['starttijd datum'])
            end_time = pd.to_datetime(row['eindtijd datum'])
            charge_time_hours = (end_time - start_time).total_seconds() / 3600
            energy_added_kWh = min(charge_time_hours * charge_rate_kW, max_usable_capacity_kWh)
            return -energy_added_kWh
        else:
            return (0.7 + 2.5) / 2 * distance_km

    # Voeg de energieverbruik kolom toe
    df['energieverbruik nieuw'] = df.apply(calculate_energy_usage, axis=1)

    # Controleer of de 'Index' kolom al bestaat voordat je deze toevoegt
    if 'Index' not in df.columns:
        df.insert(0, 'Index', range(1, len(df) + 1))

    df.drop(columns=['Unnamed: 0'], inplace=True, errors='ignore')
    return df

def status(omloopplanning_df, original_capacity, SOH):
    """
    Maak een nieuwe dataframe waarin de de huidige enrgie per rit per omloop word gegeven, 
    met een status kolom die aangeeft of de waarde onder de State of Charge komt of niet. Zo kan je controlleren
    of de oplaadtijden kloppen. Je krijgt ook een aangepast overzicht terug. 

    DE VARIABLEN:
    omloopplanning_df : de omloopplanning gelezen en in een dataframe
    original_capacity = Originele capaciteit in kWh
    SOH_min = State of Health minimale waarde (factor)
    SOH_max = State of Health maximale waarde (factor)
    min_SOC_percentage = State of Charge minimale waarde (factor)
    """
    current_capacity = original_capacity * 0.9 * SOH # Bereken de huidige accucapaciteit gebaseerd op SOH
    min_SOH_kWh = original_capacity * 0.10 * SOH # Minimale SOC in kWh

   
    omloopplanning_df['Huidige energie'] = 0.0 # Kolom voor de huidige hoeveelheid energie 
    omloopplanning_df['Status'] = '' # kolom voor de status voor het opladen
    
    bussoort = omloopplanning_df.groupby('omloop nummer') # Groepeer op buslijn
    df_lijst = [] # Lege lijst om de dataframes voor elke omloop op te slaan
    
    for soort, groep in bussoort: # Loop door elke omloop
        current_SOC = current_capacity # Begin met een volle accu voor elke omloop

    
        for index, row in groep.iterrows(): # Itereer door elke rij binnen de huidige omloop
            verbruik = row['energieverbruik nieuw']
            current_SOC -= verbruik  # Trek het verbruik van de SOC af
        
            groep.at[index, 'Huidige energie'] = current_SOC # Sla de huidige energie op in de dataframe
        
            if current_SOC < min_SOH_kWh: # Controleer of de SOC onder het minimum komt
                groep.at[index, 'Status'] = 'Opladen nodig' # Wel, daar gaat het fout, er moest opgeladen worden
            else:
                groep.at[index, 'Status'] = 'OK' # Niet, dat is goed, de planning hier klopt

        df_lijst.append(groep) # Voeg de bewerkte groep toe aan de lijst

   
    omloopplanning_df = pd.concat(df_lijst) # Gooi alle losse dataframes bij elkaar tot een grote dataframe

    
    pd.set_option('display.max_rows', None) # Toon de eerste 100 rijen van de aangepaste dataframe
    # Overzicht_df = (omloopplanning_df[['omloop nummer', 'energieverbruik', 'Huidige energie', 'Status']].head(30))
    return(omloopplanning_df)

def visualiseer_omloopplanning_met_oplaadmarkering(Gelezen_document):

    """
    Visualiseert de omloopplanning met markeringen voor opladen waar nodig.
    
    Parameters:
    Gelezen_document (pd.DataFrame): DataFrame met omloopplanning.
    
    Returns:
    fig, ax: Matplotlib figuur en as objecten voor verdere bewerking indien nodig.
    """
    # Verwijder onzichtbare spaties rondom de kolomnamen
    df = Gelezen_document
    df.columns = df.columns.str.strip()

    # Zet start- en eindtijden om naar datetime voor plotten
    df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
    df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])

    # Kleurmapping voor de verschillende activiteiten
    color_map = {
        ('dienst rit', 'ehvapt', 'ehvbst'): ('#4682B4', 0.8),    # dienst rit heenrit (darker blue)
        ('dienst rit', 'ehvbst', 'ehvapt'): ('#6495ED', 0.8),    # dienst rit terugrit (lighter blue)
        ('materiaal rit', 'ehvapt', 'ehvbst'): ('#FFA500', 0.9), # materiaal rit eindigt bij ehvbst (darker yellow)
        ('materiaal rit', 'ehvbst', 'ehvapt'): ('#FFC107', 0.7), # materiaal rit eindigt bij ehvapt (lighter yellow)
        'idle': 'lightgrey',                                     # idle (light grey)
        'opladen': '#00EE00',                                    # opladen (green)
        'unmapped': '#C1FFC1'                                    # materiaalrit naar oplaadpunt (light green)
    }

    # Begin met plotten
    fig, ax = plt.subplots(figsize=(12, 8))
    y_labels = []
    y_pos = 0  # Verticale positie voor elke unieke omloop

    # Lijst om het bereik en laagste energieverbruik bij te houden voor opladen-ranges
    opladen_ranges = []

    # Voor elke unieke omloop plotten we de activiteiten
    for run in df['omloop nummer'].unique():
        run_data = df[df['omloop nummer'] == run]
        y_labels.append(f'Run {int(run)}')
        in_sequence = False  # Om te controleren of we in een reeks "Opladen nodig" ritten zitten
        start_x, end_x = None, None  # Start- en eindtijden van de reeks "Opladen nodig" ritten
        start_index, end_index = None, None  # Start- en eindindex van de reeks "Opladen nodig" ritten
        
        for i, row in run_data.iterrows():
            # Kies kleur op basis van activiteit en route, gebruik 'unmapped' als fallback
            color = color_map.get((row['activiteit'], row['startlocatie'], row['eindlocatie']), 
                                  color_map.get(row['activiteit'], color_map['unmapped']))
            
            # Teken een balk voor de duur van de activiteit
            ax.barh(y_pos, row['eindtijd datum'] - row['starttijd datum'], left=row['starttijd datum'], color=color)
            
            # Controleer of de rit de status 'Opladen nodig' heeft
            if row['Status'] == 'Opladen nodig':
                # Voeg een doorzichtige rode overlay toe voor ritten waar opladen nodig is
                if not in_sequence:
                    # Start een nieuw rood gebied
                    start_x = row['starttijd datum']
                    start_index = i
                    in_sequence = True
                end_x = row['eindtijd datum']  # Update eindtijd voor de huidige reeks
                end_index = i  # Update eindindex voor de huidige reeks
            else:
                # Sluit een reeks "Opladen nodig" ritten af en teken de rand
                if in_sequence:
                    # Sla het volledige rode gebied op als één object
                    red_patch = ax.barh(y_pos, end_x - start_x, left=start_x, color='darkred', alpha=0.5)
                    opladen_ranges.append((red_patch[0], start_index, end_index))
                    
                    # Teken de rand om het rode gebied
                    ax.plot([start_x, end_x], [y_pos + 0.4, y_pos + 0.4], color='red', linewidth=2)  # Bovenlijn
                    ax.plot([start_x, end_x], [y_pos - 0.4, y_pos - 0.4], color='red', linewidth=2)  # Onderlijn
                    ax.plot([start_x, start_x], [y_pos - 0.4, y_pos + 0.4], color='red', linewidth=2)  # Linkerlijn
                    ax.plot([end_x, end_x], [y_pos - 0.4, y_pos + 0.4], color='red', linewidth=2)  # Rechterlijn
                    in_sequence = False  # Reset de reeks status
            
        # Als een reeks nog niet afgesloten is aan het einde van de omloop, sluit deze af
        if in_sequence:
            red_patch = ax.barh(y_pos, end_x - start_x, left=start_x, color='darkred', alpha=0.5)
            opladen_ranges.append((red_patch[0], start_index, end_index))
            
            # Teken de rand om het rode gebied
            ax.plot([start_x, end_x], [y_pos + 0.4, y_pos + 0.4], color='red', linewidth=2)  # Bovenlijn
            ax.plot([start_x, end_x], [y_pos - 0.4, y_pos - 0.4], color='red', linewidth=2)  # Onderlijn
            ax.plot([start_x, start_x], [y_pos - 0.4, y_pos + 0.4], color='red', linewidth=2)  # Linkerlijn
            ax.plot([end_x, end_x], [y_pos - 0.4, y_pos + 0.4], color='red', linewidth=2)  # Rechterlijn

        # Verhoog de verticale positie voor de volgende omloop
        y_pos += 1

    # Stel labels en as-instellingen in
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Time")
    ax.set_ylabel("Busses")

    # Stel de limieten van de x-as in om de volledige periode te tonen
    ax.set_xlim([
        df['starttijd datum'].min() - pd.Timedelta(hours=0.5),
        df['eindtijd datum'].max() + pd.Timedelta(hours=0.5)
    ])

    # Legenda voor de kleuren
    legend_elements = [
        Patch(facecolor='#4682B4', label='regular trip ehvapt -> ehvbst'),
        Patch(facecolor='#6495ED', label='regular trip ehvbst -> ehvapt'),
        Patch(facecolor='#FF8C00', label='deadhead trip ehvapt -> ehvbst'),
        Patch(facecolor='#FFD700', label='deadhead trip ehvbst -> ehvapt'),
        Patch(facecolor='lightgrey', label='idle'),
        Patch(facecolor='#00EE00', label='charging'),
        Patch(facecolor='#C1FFC1', label='material trip to garage'),
        Patch(facecolor='darkred', alpha = 0.5, edgecolor='red', label='charging needed (marked)', linewidth=2)
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Formatteer de x-as om tijd weer te geven
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
   
    # Laat de titel en rasterinstellingen zien
    plt.title("Bus Planning Gantt Chart")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()  # Optimaliseert de ruimte-indeling


    plt.show()
    return fig, ax






