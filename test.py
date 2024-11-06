import pandas as pd

# Functie om een nieuwe rit toe te voegen aan een omloop
def rit_toevoegen(omloop: pd.DataFrame, dienstregeling_rij: pd.Series, omloop_nr: int):
    nieuwe_rit = pd.DataFrame(
        {
            'startlocatie': [dienstregeling_rij['startlocatie']],
            'eindlocatie': [dienstregeling_rij['eindlocatie']],
            'starttijd': [dienstregeling_rij['vertrektijd']],
            'eindtijd': [dienstregeling_rij['eindtijd']],
            'activiteit': ['dienst rit'],
            'buslijn': [dienstregeling_rij['buslijn']],
            'energieverbruik': [0],
            'starttijd datum': [dienstregeling_rij['vertrektijd']],
            'eindtijd datum': [dienstregeling_rij['eindtijd']],
            'omloop nummer': [omloop_nr],
            'Huidige energie': [200]
        }
    )
    if not nieuwe_rit.empty:
        return pd.concat([omloop, nieuwe_rit], ignore_index=True)
    else:
        return omloop

# Functie om enkele rit in de huidige omloop samen te voegen met de vorige omloop als dat mogelijk is
def merge_single_trip_if_possible(omlopen, omloop_nr):
    # Controleer of de huidige omloop slechts één rit bevat en een vorige omloop bestaat
    if len(omlopen[omloop_nr]) == 1 and omloop_nr > 1:
        laatste_rit_omloop = omlopen[omloop_nr - 1].iloc[-1]
        eerste_rit_nieuwe_omloop = omlopen[omloop_nr].iloc[0]
        
        # Check op aansluitende locaties en tijden
        if (laatste_rit_omloop['eindlocatie'] == eerste_rit_nieuwe_omloop['startlocatie'] and
                laatste_rit_omloop['eindtijd'] <= eerste_rit_nieuwe_omloop['starttijd']):
            
            # Wijzig omloop nummer van de enkele rit in nieuwe omloop
            omlopen[omloop_nr].loc[:, 'omloop nummer'] = omloop_nr - 1
            
            # Voeg de nieuwe omloop samen met de vorige omloop en verwijder de nieuwe omloop
            omlopen[omloop_nr - 1] = pd.concat([omlopen[omloop_nr - 1], omlopen[omloop_nr]], ignore_index=True)
            del omlopen[omloop_nr]

# Data inladen
omloopplanning = pd.read_excel('omloopplanning.xlsx')
afstandsmatrix = pd.read_excel('Connexxion data - 2024-2025.xlsx', sheet_name='Afstandsmatrix')
dienstregeling = pd.read_excel('Connexxion data - 2024-2025.xlsx', sheet_name='Dienstregeling')

# Dienstregeling voorbereiden
dienstregeling['vertrektijd'] = pd.to_datetime(dienstregeling['vertrektijd'], format='%H:%M', errors='coerce')
dienstregeling = dienstregeling.merge(
    afstandsmatrix[['startlocatie', 'eindlocatie', 'max reistijd in min', 'buslijn']],
    on=['startlocatie', 'eindlocatie', 'buslijn'],
    how='left'
)
dienstregeling['eindtijd'] = dienstregeling['vertrektijd'] + pd.to_timedelta(dienstregeling['max reistijd in min'], unit='m')
dienstregeling['early_morning'] = dienstregeling['vertrektijd'].dt.hour < 5
dienstregeling['vertrektijd'] += pd.to_timedelta(1, unit="days") * dienstregeling['early_morning']
dienstregeling['eindtijd'] += pd.to_timedelta(1, unit="days") * dienstregeling['early_morning']
dienstregeling = dienstregeling.sort_values(by=['early_morning', 'vertrektijd']).reset_index(drop=True)
dienstregeling = dienstregeling.drop(columns=['early_morning'])

# Variabelen initialiseren
omlopen = {}
omloop_nr = 1 

# Hoofd lus voor inroosteren
while len(dienstregeling) > 0:
    # Nieuwe omloop initialiseren
    omlopen[omloop_nr] = pd.DataFrame(columns=[
        'startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'activiteit', 
        'buslijn', 'energieverbruik', 'starttijd datum', 'eindtijd datum', 'omloop nummer', 'Huidige energie'
    ])
    omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.iloc[0], omloop_nr)
    
    # Verwijder de eerste rij uit dienstregeling en reset de index
    dienstregeling = dienstregeling.drop(dienstregeling.index[0]).reset_index(drop=True)
    
    i = 1
    while i < len(dienstregeling):
        omloop_laatste_rit_index = len(omlopen[omloop_nr]) - 1
        aankomsttijd_vorige_rit = omlopen[omloop_nr].iloc[omloop_laatste_rit_index]['eindtijd']
        vertrektijd_dienstrit = dienstregeling.iloc[i]['vertrektijd']
        tijd_voor_uit_en_instappen = pd.Timedelta(1, unit="minute")
        huidige_locatie_bus = omlopen[omloop_nr].iloc[omloop_laatste_rit_index]['eindlocatie']
        startlocatie_dienstregeling = dienstregeling.iloc[i]['startlocatie']
        
        # Controle of de bus op tijd en op de juiste locatie is
        if huidige_locatie_bus == startlocatie_dienstregeling and aankomsttijd_vorige_rit <= vertrektijd_dienstrit - tijd_voor_uit_en_instappen:
            omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.iloc[i], omloop_nr)
            dienstregeling = dienstregeling.drop(dienstregeling.index[i]).reset_index(drop=True)
        else:
            i += 1

    # Probeer enkele rit samen te voegen indien mogelijk
    merge_single_trip_if_possible(omlopen, omloop_nr)
    
    # Omloopnummer verhogen voor de volgende iteratie
    omloop_nr += 1

# Concateneer alle omlopen in één DataFrame
omloop_df = pd.concat([omlopen[i] for i in range(1, len(omlopen) + 1)], ignore_index=True)


# Omlopen afdrukken voor controle
#for i in omlopen:
#   print(f'omloop {i}: ')
#   print(omlopen[i])
#    print("")

# Visualiseer omloopplanning met de VisualisatieOmloopplanning-module (als die beschikbaar is)
import VisualisatieOmloopplanning as VC
# VC.Visualiatie(omloop_df)

import acuucapaciteit as AC
omloop_df = AC.Afstand_omloop_toevoegen(omloop_df, afstandsmatrix)
omloop_df = AC.add_energy_usage_column(omloop_df)

omloop_df.to_excel("nieuwe_planning.xlsx", index=False)
