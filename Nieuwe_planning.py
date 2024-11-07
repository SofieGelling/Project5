import pandas as pd

# lees data
omloopplanning = pd.read_excel('omloopplanning.xlsx')
afstandsmatrix = pd.read_excel('Connexxion data - 2024-2025.xlsx', sheet_name='Afstandsmatrix')
dienstregeling = pd.read_excel('Connexxion data - 2024-2025.xlsx', sheet_name='Dienstregeling')

def rit_toevoegen(omloop:pd.DataFrame, dienstregeling_rij:pd.DataFrame, omloop_nr:int):
    rit_dienstregeling = dienstregeling_rij
    nieuwe_rit = pd.DataFrame(
        {
            'startlocatie': rit_dienstregeling['startlocatie'],
            'eindlocatie': rit_dienstregeling['eindlocatie'],
            'starttijd': rit_dienstregeling['vertrektijd'],
            'eindtijd': rit_dienstregeling['eindtijd'],
            'activiteit': 'dienst rit',
            'buslijn': rit_dienstregeling['buslijn'],
            'energieverbruik': 0,
            'starttijd datum': rit_dienstregeling['vertrektijd'],
            'eindtijd datum': rit_dienstregeling['eindtijd'],
            'omloop nummer': omloop_nr,
            'Huidige energie': 200
        },
        [0]
    )
    return pd.concat([omloop, nieuwe_rit])

# Convert 'vertrektijd' column to datetime, with error handling
dienstregeling['vertrektijd'] = pd.to_datetime(dienstregeling['vertrektijd'], format='%H:%M', errors='coerce')

# Merge dienstregeling with afstandsmatrix on 'startlocatie', 'eindlocatie', and 'buslijn' to get max reistijd in min
dienstregeling = dienstregeling.merge(
    afstandsmatrix[['startlocatie', 'eindlocatie', 'max reistijd in min', 'buslijn']], 
    on=['startlocatie', 'eindlocatie', 'buslijn'], 
    how='left'
)
dienstregeling['eindtijd'] = dienstregeling['vertrektijd'] + pd.to_timedelta(dienstregeling['max reistijd in min'], unit='m')
dienstregeling['early_morning'] = dienstregeling['vertrektijd'].dt.hour < 5
dienstregeling['vertrektijd'] = dienstregeling['vertrektijd'] + pd.to_timedelta(1, unit="days") * dienstregeling['early_morning']
dienstregeling['eindtijd'] = dienstregeling['eindtijd'] + pd.to_timedelta(1, unit="days") * dienstregeling['early_morning']
dienstregeling = dienstregeling.sort_values(by=['early_morning', 'vertrektijd']).reset_index(drop=True)
dienstregeling = dienstregeling.drop(columns=['early_morning'])

# print debug
#print(dienstregeling)
#input("druk op een toets om door te gaan")

#'lijst' met omlopen (dictionary omdat we starten 1 ipv 0)
omlopen:dict[pd.DataFrame]
omlopen = {}

#het nummer van de eerte omloop
omloop_nr = 1 

#blijft een omloop toevoegen zolang het nodig is
while len(dienstregeling) > 0: #dit is de goeie
    highest_index_dienstregeling = len(dienstregeling) - 1
    #voeg de eerste rit voor deze omloop toe
    i = 0
    omlopen[omloop_nr] = pd.DataFrame({'startlocatie': [], 'eindlocatie': [], 'starttijd': [], 'eindtijd': [], 'activiteit': [], 'buslijn': [], 'energieverbruik': [], 'starttijd datum': [], 'eindtijd datum': [], 'omloop nummer':[], 'Huidige energie': []})
    omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.loc[0], omloop_nr)
    
    # #debug print
    # print(len(dienstregeling))
    # print(f"omloop_nr: {omloop_nr}, i: {i}, aankomsttijd_vorige_rit: {'xxxx-xx-xx --:--:--'}, vertrektijd_dienstrit: {dienstregeling.at[0, 'vertrektijd']}, huidige_locatie_bus: {'------'}, startlocatie_dienstregeling: {dienstregeling.at[0, 'eindlocatie']}")
    
    dienstregeling.drop(0, inplace=True)
    i = 1
    
    #blijf ritten aan deze omloop toevoegen tot alle dienstritten zijn bekeken.
    while i <= highest_index_dienstregeling and len(dienstregeling) > 0:
        # berekeningen
        
        omloop_laatste_rit_index = len(omlopen[omloop_nr])-1
        aankomsttijd_vorige_rit = omlopen[omloop_nr].at[omloop_laatste_rit_index, 'eindtijd']
        vertrektijd_dienstrit = dienstregeling.at[i, 'vertrektijd']
        huidige_locatie_bus = omlopen[omloop_nr].at[omloop_laatste_rit_index, 'eindlocatie']
        startlocatie_dienstregeling = dienstregeling.at[i, 'startlocatie']
        
        # voeg de rit toe als de bus op tijd is en op de juiste plek
        if huidige_locatie_bus == startlocatie_dienstregeling and aankomsttijd_vorige_rit <= vertrektijd_dienstrit:
            # # debug print
            # print(f"omloop_nr: {omloop_nr}, i: {i}, aankomsttijd_vorige_rit: {aankomsttijd_vorige_rit}, vertrektijd_dienstrit: {vertrektijd_dienstrit}, huidige_locatie_bus: {huidige_locatie_bus}, startlocatie_dienstregeling: {startlocatie_dienstregeling}")
            
            omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.loc[i], omloop_nr)
            dienstregeling.drop(i, inplace=True)
            omlopen[omloop_nr].reset_index(inplace=True, drop=True)
        i = i + 1
    # # debug pauze
    # input("druk op een toets om door te gaan")
    
    dienstregeling.reset_index(inplace=True, drop=True)
    
    #het nummer van de volgende omloop
    omloop_nr = omloop_nr + 1

for i in omlopen:
    print(f'omloop {i}: ')
    print(omlopen[i])
    print("")

omloop_df = pd.concat([omlopen[i] for i in range(1, len(omlopen) + 1)])

import VisualisatieOmloopplanning as VC
VC.Visualiatie(omloop_df) 