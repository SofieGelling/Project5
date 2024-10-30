import pandas as pd
import VisualisatieOmloopplanning as VO

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

def detecteer_en_verwijder_foute_rijen(df):
    """
    Functie om rijen te detecteren waar de starttijd van een rit niet overeenkomt met de eindtijd
    van de vorige rit binnen dezelfde omloop. Deze rijen worden geprint en vervolgens verwijderd.
    
    Parameters:
    df (pd.DataFrame): DataFrame met kolommen 'starttijd datum', 'eindtijd datum' en 'omloop nummer'.
    
    Returns:
    pd.DataFrame: DataFrame zonder de foute rijen.
    """
    # Sorteer de data op 'omloop nummer' en 'starttijd datum' om de ritten op volgorde te controleren
    df = df.sort_values(by=['omloop nummer', 'starttijd datum']).reset_index(drop=True)
    foute_rijen = []  # Lijst om de indexen van foute rijen op te slaan

    for i in range(len(df) - 1):
        huidige_rit = df.iloc[i]
        volgende_rit = df.iloc[i + 1]

        # Controleer of beide ritten bij dezelfde omloop horen
        if huidige_rit['omloop nummer'] == volgende_rit['omloop nummer']:
            eindtijd_huidige = huidige_rit['eindtijd datum']
            starttijd_volgende = volgende_rit['starttijd datum']

            # Controleer of er een mismatch is tussen eindtijd en starttijd
            if starttijd_volgende != eindtijd_huidige:
                foute_rijen.append(i + 1)  # Voeg de index van de volgende rit toe aan de lijst van fouten
                # print(f"Fout gevonden op rij {i + 1}: omloop {huidige_rit['omloop nummer']}, "
                      # f"eindtijd huidige rit {eindtijd_huidige}, starttijd volgende rit {starttijd_volgende}")

    # Verwijder de foute rijen uit de DataFrame
    df = df.drop(foute_rijen).reset_index(drop=True)
    
    return df

def status(omloopplanning_df, original_capacity, SOH, min_SOC_percentage):
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
    current_capacity = original_capacity * SOH # Bereken de huidige accucapaciteit gebaseerd op SOH
    min_SOC_kWh = current_capacity * min_SOC_percentage # Minimale SOC in kWh

   
    omloopplanning_df['Huidige energie'] = 0.0 # Kolom voor de huidige hoeveelheid energie 
    omloopplanning_df['Status'] = '' # kolom voor de status voor het opladen
    
    bussoort = omloopplanning_df.groupby('omloop nummer') # Groepeer op buslijn
    df_lijst = [] # Lege lijst om de dataframes voor elke omloop op te slaan
    
    for soort, groep in bussoort: # Loop door elke omloop
        current_SOC = current_capacity # Begin met een volle accu voor elke omloop van 270 kWh

    
        for index, row in groep.iterrows(): # Itereer door elke rij binnen de huidige omloop
            verbruik = row['energieverbruik nieuw']
            current_SOC -= verbruik  # Trek het verbruik van de SOC af
        
            groep.at[index, 'Huidige energie'] = current_SOC # Sla de huidige energie op in de dataframe
        
            if current_SOC < min_SOC_kWh: # Controleer of de SOC onder het minimum komt
                groep.at[index, 'Status'] = 'Opladen nodig' # Wel, daar gaat het fout, er moest opgeladen worden
            else:
                groep.at[index, 'Status'] = 'OK' # Niet, dat is goed, de planning hier klopt

        df_lijst.append(groep) # Voeg de bewerkte groep toe aan de lijst

   
    omloopplanning_df = pd.concat(df_lijst) # Gooi alle losse dataframes bij elkaar tot een grote dataframe

    
    pd.set_option('display.max_rows', None) # Toon de eerste 100 rijen van de aangepaste dataframe
    # Overzicht_df = (omloopplanning_df[['omloop nummer', 'energieverbruik', 'Huidige energie', 'Status']].head(30))
    return(omloopplanning_df)

def filter(omloopplanning_df): # Filter de DataFrame om alleen de rijen zonder "OK" te tonen
    df_filtered = omloopplanning_df[omloopplanning_df['Status'] == 'Opladen nodig']
    return df_filtered
   
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

    # Voeg de Index kolom toe aan het begin en verwijder een eventuele 'Unnamed: 0' kolom
    df.insert(0, 'Index', range(1, len(df) + 1))
    df.drop(columns=['Unnamed: 0'], inplace=True, errors='ignore')
    return df

def tel_ritten_per_type(df):
    """
    Functie om het aantal dienstritten, materieelritten, en oplaadritten in de DataFrame te tellen.
    
    Parameters:
    df (pd.DataFrame): DataFrame met een kolom 'activiteit' waarin de soort rit staat.
    
    Returns:
    dict: Dictionary met de aantallen per type rit.
    """
    # Controleer of de kolom 'activiteit' aanwezig is in de DataFrame
    if 'activiteit' not in df.columns:
        raise ValueError("De kolom 'activiteit' ontbreekt in de DataFrame.")

    # Tel het aantal rijen per activiteit
    dienstritten = df[df['activiteit'] == 'dienst rit'].shape[0]
    materiaalritten = df[df['activiteit'] == 'materiaal rit'].shape[0]
    oplaadritten = df[df['activiteit'] == 'opladen'].shape[0]
    
    # Maak een dictionary om de resultaten overzichtelijk terug te geven
    ritten_telling = {
        'Dienstritten': dienstritten,
        'Materiaalritten': materiaalritten,
        'Oplaadritten': oplaadritten
    }
    
    print("Aantal ritten per type:")
    for rit_type, aantal in ritten_telling.items():
        print(f"{rit_type}: {aantal}")
    
    return ritten_telling

def check_oplaadtijd(df):
    # Filter de DataFrame voor alleen de opladen-activiteiten
    opladen_df = df[df['activiteit'] == 'opladen'].copy()

    # Bereken de duur in minuten
    opladen_df['duur'] = (opladen_df['eindtijd datum'] - opladen_df['starttijd datum']).dt.total_seconds() / 60

    # Filter op rijen waar de duur minder dan 15 minuten is
    korte_oplaadperiodes = opladen_df[opladen_df['duur'] < 15]

    if korte_oplaadperiodes.empty:
        print("Er zijn geen opladen-activiteiten met een duur van minder dan 15 minuten.")
    else:
        print("Opladen-activiteiten met een duur van minder dan 15 minuten:")
        print(korte_oplaadperiodes[['omloop nummer', 'starttijd datum', 'eindtijd datum', 'duur']])

def main():
    omloopplanning_df = pd.read_excel("omloopplanning.xlsx")
    connexxion_data = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name=1)

    df = voeg_idle_tijden_toe(omloopplanning_df)
    # tel_ritten_per_type(df)
    df = detecteer_en_verwijder_foute_rijen(df)
    # tel_ritten_per_type(df)
    df = voeg_idle_tijden_toe(df)
    df = Afstand_omloop_toevoegen(df, connexxion_data)
    df = add_energy_usage_column(df, soh_value=0.85)
    df = status(df, 300, 0.90, 0.10)
    df.to_excel("nieuwe_data.xlsx", index=False)
    check_oplaadtijd(df)
    print(df.columns)
    VO.visualiseer_omloopplanning_met_oplaadmarkering(df)

main()
