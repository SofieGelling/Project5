#%% OPENEN VAN HET BESTAND

import pandas as pd

omloopplanning_df = pd.read_excel("/Users/esthergellings/Desktop/School/project/Project5/omloopplanning.xlsx")
omloopplanning_df.head()

# Definieer de parameters
original_capacity = 300  # Originele accucapaciteit in kWh
SOH_min = 0.85  # Minimale SOH (State of Health)
SOH_max = 0.95  # Maximale SOH (State of Health)
min_SOC_percentage = 0.10  # Minimale SOC (State of Charge), 10%

# Simuleer een SOH waarde tussen 85% en 95%
SOH = (SOH_min + SOH_max) / 2  # Gemiddelde SOH 

# Bereken de huidige accucapaciteit gebaseerd op SOH
current_capacity = original_capacity * SOH

# Minimale SOC in kWh
min_SOC_kWh = current_capacity * min_SOC_percentage

min_SOC_kWh, current_capacity

# Voeg een kolom toe om het cumulatieve energieverbruik bij te houden en de status
omloopplanning_df['Cumulatief verbruik'] = 0
omloopplanning_df['Status'] = ''

# Groepeer op buslijn
bussoort = omloopplanning_df.groupby('omloop nummer')

# Maak een lege lijst om de dataframes voor elke buslijn op te slaan
df_lijst = []

# Loop door elke buslijngroep
for soort, groep in bussoort:
    # Begin met een volle accu voor elke buslijn van 270 kWh
    current_SOC = current_capacity

# Itereer door elke rij binnen de huidige buslijn
    for index, row in groep.iterrows():
        verbruik = row['energieverbruik']
        current_SOC -= verbruik  # Trek het verbruik van de SOC af
        
        # Sla het cumulatieve verbruik op in de dataframe
        groep.at[index, 'Cumulatief verbruik'] = current_SOC
        
        # Controleer of de SOC onder het minimum komt
        if current_SOC < min_SOC_kWh:
            groep.at[index, 'Status'] = 'Opladen nodig'
            current_SOC = current_capacity  # Simuleer opladen tot 90% van de capaciteit
        else:
            groep.at[index, 'Status'] = 'OK'

    # Voeg de bewerkte groep toe aan de lijst
    df_lijst.append(groep)

# Concateneer alle groepen om weer een volledige dataframe te krijgen
omloopplanning_df = pd.concat(df_lijst)

# Toon de eerste 100 rijen van de aangepaste dataframe
pd.set_option('display.max_rows', None)
#print(omloopplanning_df[['buslijn', 'startlocatie', 'eindlocatie', 'energieverbruik', 'Cumulatief verbruik', 'Status']].head(100))
print(omloopplanning_df[['omloop nummer', 'energieverbruik', 'Cumulatief verbruik', 'Status']].head(100))

# Filter de DataFrame om alleen de rijen zonder "OK" te tonen
#df_filtered = omloopplanning_df[omloopplanning_df['Status'] == 'Opladen nodig']

# Resultaat van gefilterde data
#print(df_filtered)
