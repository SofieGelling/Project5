import pandas as pd

# lees data
omloopplanning = pd.read_excel('omloopplanning.xlsx')
afstandsmatrix = pd.read_excel('Connexxion data - 2024-2025.xlsx', sheet_name='Afstandsmatrix')
dienstregeling = pd.read_excel('Connexxion data - 2024-2025.xlsx', sheet_name='Dienstregeling')


def Twee_dataframes(dienstregeling, afstandsmatrix):
    # Convert 'vertrektijd' column to datetime, with error handling
    dienstregeling['vertrektijd'] = pd.to_datetime(dienstregeling['vertrektijd'], format='%H:%M', errors='coerce')
    # Drop rows where 'vertrektijd' could not be converted
    dienstregeling = dienstregeling.dropna(subset=['vertrektijd']) #dit moet misschien niet          <<-------------------

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

#de hele dienstregeling moeten we blijkbaar gebruiken, anders vertrekt een bus vanuit het station en heeft hij in airport niks meer te doen
# Het volgende heb ik even gekopiëerd vanuit hierboven:

# Convert 'vertrektijd' column to datetime, with error handling
dienstregeling['vertrektijd'] = pd.to_datetime(dienstregeling['vertrektijd'], format='%H:%M', errors='coerce')
# Drop rows where 'vertrektijd' could not be converted
dienstregeling = dienstregeling.dropna(subset=['vertrektijd']) #dit moet misschien niet          <<-------------------

# Merge dienstregeling with afstandsmatrix on 'startlocatie', 'eindlocatie', and 'buslijn' to get max reistijd in min
dienstregeling = dienstregeling.merge(
    afstandsmatrix[['startlocatie', 'eindlocatie', 'max reistijd in min', 'buslijn']], 
    on=['startlocatie', 'eindlocatie', 'buslijn'], 
    how='left'
)
dienstregeling['eindtijd'] = dienstregeling['vertrektijd'] + pd.to_timedelta(dienstregeling['max reistijd in min'], unit='m')
dienstregeling['early_morning'] = dienstregeling['vertrektijd'].dt.hour < 5
dienstregeling = dienstregeling.sort_values(by=['early_morning', 'vertrektijd']).reset_index(drop=True)
dienstregeling = dienstregeling.drop(columns=['early_morning'])

# print debug
#print(dienstregeling)
#input("druk op een toets om door te gaan")

#'lijst' met omlopen (dictionary omdat we starten 1 ipv 0)
omlopen = {}

#het nummer van de eerte omloop
omloop_nr = 1 

#blijft een omloop toevoegen zolang het nodig is
while len(dienstregeling) > 0: #dit is de goeie
# while len(dienstregeling) > 18: #dit is om te testen want er gaat iets mis
    #voeg de eerste rit voor deze omloop toe
    i = 0
    omlopen[omloop_nr] = pd.DataFrame({'startlocatie': [], 'eindlocatie': [], 'starttijd': [], 'eindtijd': [], 'activiteit': [], 'buslijn': [], 'energieverbruik': [], 'starttijd datum': [], 'eindtijd datum': [], 'omloop nummer':[], 'Huidige energie': []})
    omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.iloc[0], 1)
    
    # #debug print
    # print(len(dienstregeling))
    # print(f"omloop_nr: {omloop_nr}, i: {i}, aankomsttijd_vorige_rit: {'xxxx-xx-xx --:--:--'}, vertrektijd_dienstrit: {dienstregeling.at[0, 'vertrektijd']}, huidige_locatie_bus: {'------'}, startlocatie_dienstregeling: {dienstregeling.at[0, 'eindlocatie']}")
    
    dienstregeling.drop(0, inplace=True)
    omlopen[omloop_nr].reset_index(inplace=True, drop=True)
    dienstregeling.reset_index(inplace=True, drop=True)
    i = 1
    
    #blijf ritten aan deze omloop toevoegen tot alle dienstritten zijn bekeken.
    while i < len(dienstregeling) and len(dienstregeling) > 0:
        # berekeningen
        omloop_laatste_rit_index = len(omlopen[omloop_nr])-1
        aankomsttijd_vorige_rit = omlopen[omloop_nr].at[omloop_laatste_rit_index, 'eindtijd']
        vertrektijd_dienstrit = dienstregeling.at[i, 'vertrektijd']
        tijd_voor_uit_en_instappen = pd.Timedelta(1, unit="minute")
        huidige_locatie_bus = omlopen[omloop_nr].at[omloop_laatste_rit_index, 'eindlocatie']
        startlocatie_dienstregeling = dienstregeling.at[i, 'startlocatie']
        
        # voeg de rit toe als de bus op tijd is en op de juiste plek
        if huidige_locatie_bus == startlocatie_dienstregeling and aankomsttijd_vorige_rit <= vertrektijd_dienstrit - tijd_voor_uit_en_instappen:
            # # debug print
            # print(f"omloop_nr: {omloop_nr}, i: {i}, aankomsttijd_vorige_rit: {aankomsttijd_vorige_rit}, vertrektijd_dienstrit: {vertrektijd_dienstrit}, huidige_locatie_bus: {huidige_locatie_bus}, startlocatie_dienstregeling: {startlocatie_dienstregeling}")
            
            omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.iloc[i], 1)
            dienstregeling.drop(i, inplace=True)
            omlopen[omloop_nr].reset_index(inplace=True, drop=True)
            dienstregeling.reset_index(inplace=True, drop=True)
        i = i + 1
    # # debug pauze
    # input("druk op een toets om door te gaan")
    
    #het nummer van de volgende omloop
    omloop_nr = omloop_nr + 1

for i in omlopen:
    print(f'omloop {i}: ')
    print(omlopen[i])
    print("")