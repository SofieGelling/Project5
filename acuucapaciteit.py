#%% OPENEN VAN HET BESTAND

import pandas as pd

def lezen_bestand(filepath):
    """
    Laad het excel bestand met de omloopplanning in een dataframe.
    filepath : pad naar het excelbestand
    omloopplanning_df : de omloopplanning gelezen en in een dataframe
    """
    omloopplanning_df = pd.read_excel(filepath)
    return omloopplanning_df

def status(omloopplanning_df, original_capacity, SOH_min, SOH_max, min_SOC_percentage):
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
    SOH = (SOH_min + SOH_max) / 2  # Gemiddelde SOH 
    current_capacity = original_capacity * SOH # Bereken de huidige accucapaciteit gebaseerd op SOH
    min_SOC_kWh = current_capacity * min_SOC_percentage # Minimale SOC in kWh

   
    omloopplanning_df['Huidige energie'] = 0.0 # Kolom voor de huidige hoeveelheid energie 
    omloopplanning_df['Status'] = '' # kolom voor de status voor het opladen
    
    bussoort = omloopplanning_df.groupby('omloop nummer') # Groepeer op buslijn
    df_lijst = [] # Lege lijst om de dataframes voor elke omloop op te slaan
    
    for soort, groep in bussoort: # Loop door elke omloop
        current_SOC = current_capacity # Begin met een volle accu voor elke omloop van 270 kWh

    
        for index, row in groep.iterrows(): # Itereer door elke rij binnen de huidige omloop
            verbruik = row['energieverbruik']
            current_SOC -= verbruik  # Trek het verbruik van de SOC af
        
            groep.at[index, 'Huidige energie'] = current_SOC # Sla de huidige energie op in de dataframe
        
            if current_SOC < min_SOC_kWh: # Controleer of de SOC onder het minimum komt
                groep.at[index, 'Status'] = 'Opladen nodig' # Wel, daar gaat het fout, er moest opgeladen worden
                current_SOC = current_capacity  # Simuleer opladen tot 90% van de capaciteit
            else:
                groep.at[index, 'Status'] = 'OK' # Niet, dat is goed, de planning hier klopt

        df_lijst.append(groep) # Voeg de bewerkte groep toe aan de lijst

   
    omloopplanning_df = pd.concat(df_lijst) # Gooi alle losse dataframes bij elkaar tot een grote dataframe

    
    pd.set_option('display.max_rows', None) # Toon de eerste 100 rijen van de aangepaste dataframe
    # Overzicht_df = (omloopplanning_df[['omloop nummer', 'energieverbruik', 'Huidige energie', 'Status']].head(30))
    return(omloopplanning_df)

def filter(omloopplanning_df): # Filter de DataFrame om alleen de rijen zonder "OK" te tonen
    df_filtered = omloopplanning_df[omloopplanning_df['Status'] == 'Opladen nodig']
    return print(df_filtered)
    
"""
original_capacity = 300  -- Originele accucapaciteit in kWh
SOH_min = 0.85  -- Minimale SOH (State of Health)
SOH_max = 0.95  -- Maximale SOH (State of Health)
min_SOC_percentage = 0.10  -- Minimale SOC (State of Charge), 10%
 """

omloopplanning_df = lezen_bestand("/Users/esthergellings/Desktop/School/project/Project5/omloopplanning.xlsx")
omloopplanning = status(omloopplanning_df, 300, 0.85, 0.95, 0.10)
Overzicht_df = (omloopplanning[['omloop nummer', 'energieverbruik', 'Huidige energie', 'Status']].head(200))
print(Overzicht_df)
Gefilterd = filter(Overzicht_df)