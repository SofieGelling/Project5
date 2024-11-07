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

# Functie om materiaalritten toe te voegen aan het begin en einde van elke omloop in omloop_df
def voeg_materiaalritten_toe_aan_omlopen(omloop_df):
    nieuwe_rijen = []

    for omloop_nr in omloop_df['omloop nummer'].unique():
        omloop_data = omloop_df[omloop_df['omloop nummer'] == omloop_nr]
        
        # Materiaalrit toevoegen aan het begin
        eerste_rit = omloop_data.iloc[0]
        locatie_start = eerste_rit['startlocatie']
        
        if locatie_start == 'ehvbst':
            tijd_in_minuten = 4
        elif locatie_start == 'ehvapt':
            tijd_in_minuten = 20
        else:
            raise ValueError("Onbekende locatie voor de materiaalrit")

        starttijd = eerste_rit['starttijd datum'] - pd.Timedelta(minutes=tijd_in_minuten)
        eindtijd = eerste_rit['starttijd datum']
        nieuwe_rijen.append({
            'startlocatie': 'ehvgar',
            'eindlocatie': locatie_start,
            'starttijd': starttijd,
            'eindtijd': eindtijd,
            'activiteit': 'materiaal rit',
            'buslijn': None,
            'energieverbruik': 0,
            'starttijd datum': starttijd,
            'eindtijd datum': eindtijd,
            'omloop nummer': omloop_nr,
            'Huidige energie': 200
        })

        # Materiaalrit toevoegen aan het einde
        laatste_rit = omloop_data.iloc[-1]
        locatie_eind = laatste_rit['eindlocatie']
        
        if locatie_eind == 'ehvbst':
            tijd_in_minuten = 4
        elif locatie_eind == 'ehvapt':
            tijd_in_minuten = 20
        else:
            raise ValueError("Onbekende locatie voor de materiaalrit")

        starttijd = laatste_rit['eindtijd datum']
        eindtijd = starttijd + pd.Timedelta(minutes=tijd_in_minuten)
        nieuwe_rijen.append({
            'startlocatie': locatie_eind,
            'eindlocatie': 'ehvgar',
            'starttijd': starttijd,
            'eindtijd': eindtijd,
            'activiteit': 'materiaal rit',
            'buslijn': None,
            'energieverbruik': 0,
            'starttijd datum': starttijd,
            'eindtijd datum': eindtijd,
            'omloop nummer': omloop_nr,
            'Huidige energie': 200
        })
    # Voeg de nieuwe materiaalritten toe aan omloop_df en sorteert deze opnieuw op omloopnummer en starttijd
    materiaalritten_df = pd.DataFrame(nieuwe_rijen)
    omloop_df = pd.concat([omloop_df, materiaalritten_df], ignore_index=True)
    omloop_df = omloop_df.sort_values(by=['omloop nummer', 'starttijd datum']).reset_index(drop=True)
    return omloop_df

# Functie om oplaadmomenten op het begin en einde toe te voegen
def voeg_oplaad_momenten_toe(omloop, omloop_nr):
    # Stap 1: Bepaal de laatste rit en de locatie waar de rit eindigt
    laatste_rit = omloop.iloc[-1]
    nieuwe_rijen = []

    # Stap 2: Voeg een materiaalrit toe naar de garage
    # Controleer of de laatste eindlocatie 'ehvapt' of 'ehvbst' is om de reistijd naar de garage in te stellen
    if laatste_rit['eindlocatie'] == 'ehvapt':
        tijd_naar_garage = 20  # Tijd in minuten naar de garage
        terug_locatie = 'ehvapt'
    elif laatste_rit['eindlocatie'] == 'ehvbst':
        tijd_naar_garage = 4  # Kortere tijd naar de garage vanaf 'ehvbst'
        terug_locatie = 'ehvbst'
    else:
        raise ValueError("Onbekende eindlocatie voor de materiaalrit")  # Foutafhandeling voor ongekende locatie

    # Stap 3: Bereken de tijden en voeg de materiaalrit naar de garage toe
    starttijd_naar_garage = laatste_rit['eindtijd datum']
    eindtijd_naar_garage = starttijd_naar_garage + pd.Timedelta(minutes=tijd_naar_garage)
    nieuwe_rijen.append({
        'startlocatie': laatste_rit['eindlocatie'],
        'eindlocatie': 'ehvgar',
        'starttijd': starttijd_naar_garage.time(),
        'eindtijd': eindtijd_naar_garage.time(),
        'activiteit': 'materiaal rit',
        'buslijn': None,
        'energieverbruik': 0,
        'starttijd datum': starttijd_naar_garage,
        'eindtijd datum': eindtijd_naar_garage,
        'omloop nummer': omloop_nr
    })

    # Stap 4: Voeg een oplaadperiode toe (30 minuten opladen in de garage)
    starttijd_opladen = eindtijd_naar_garage
    eindtijd_opladen = starttijd_opladen + pd.Timedelta(minutes=30)
    nieuwe_rijen.append({
        'startlocatie': 'ehvgar',
        'eindlocatie': 'ehvgar',
        'starttijd': starttijd_opladen.time(),
        'eindtijd': eindtijd_opladen.time(),
        'activiteit': 'opladen',
        'buslijn': None,
        'energieverbruik': 0,  # Energie wordt later door AC bijgewerkt
        'starttijd datum': starttijd_opladen,
        'eindtijd datum': eindtijd_opladen,
        'omloop nummer': omloop_nr
    })

    # Stap 5: Voeg een materiaalrit terug naar de oorspronkelijke locatie toe
    starttijd_terug = eindtijd_opladen
    eindtijd_terug = starttijd_terug + pd.Timedelta(minutes=tijd_naar_garage)
    nieuwe_rijen.append({
        'startlocatie': 'ehvgar',
        'eindlocatie': terug_locatie,
        'starttijd': starttijd_terug.time(),
        'eindtijd': eindtijd_terug.time(),
        'activiteit': 'materiaal rit',
        'buslijn': None,
        'energieverbruik': 0,
        'starttijd datum': starttijd_terug,
        'eindtijd datum': eindtijd_terug,
        'omloop nummer': omloop_nr
    })

    # Voeg de nieuwe rijen toe aan de omloop en retourneer de bijgewerkte omloop
    return pd.concat([omloop, pd.DataFrame(nieuwe_rijen)], ignore_index=True)

# Functie om de lossen ritten in elkaar te voegen
def verplaats_rit_met_index_aanpassing(omloop: pd.DataFrame, oude_index: int, nieuwe_index: int) -> pd.DataFrame:
    """
    Verplaatst een rit in het omloop-DataFrame van oude_index naar nieuwe_index.
    Past de index van het DataFrame aan om de juiste volgorde te behouden.
    
    Parameters:
    - omloop (pd.DataFrame): Het DataFrame met de omloop waarin de ritten zijn opgeslagen.
    - oude_index (int): De huidige index van de rit die je wilt verplaatsen.
    - nieuwe_index (int): De nieuwe index waar je de rit wilt plaatsen.
    
    Returns:
    - pd.DataFrame: Een nieuw DataFrame met de verplaatste rit en bijgewerkte index.
    """
    # Controleer of indices binnen het bereik van de DataFrame liggen
    if oude_index < 0 or oude_index >= len(omloop):
        raise IndexError("oude_index ligt buiten het bereik van het DataFrame.")
    if nieuwe_index < 0 or nieuwe_index > len(omloop):
        raise IndexError("nieuwe_index ligt buiten het bereik van het DataFrame.")
    
    # Haal de rit op die verplaatst moet worden
    rit = omloop.iloc[oude_index]
    
    # Verwijder de rit van de oude positie
    omloop = omloop.drop(omloop.index[oude_index]).reset_index(drop=True)
    
    # Voeg de rit in op de nieuwe positie
    bovenste_gedeelte = omloop.iloc[:nieuwe_index]
    onderste_gedeelte = omloop.iloc[nieuwe_index:]
    
    # Construeer het nieuwe DataFrame met de verplaatste rit op de juiste plek
    omloop = pd.concat([bovenste_gedeelte, rit.to_frame().T, onderste_gedeelte], ignore_index=True)
    
    # Reset de index van het DataFrame om de volgorde bij te werken
    omloop.reset_index(drop=True, inplace=True)
    
    return omloop


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
    dienstritten_teller = 0

    while i < len(dienstregeling):
        omloop_laatste_rit_index = len(omlopen[omloop_nr]) - 1
        aankomsttijd_vorige_rit = omlopen[omloop_nr].iloc[omloop_laatste_rit_index]['eindtijd datum']
        vertrektijd_dienstrit = dienstregeling.iloc[i]['vertrektijd']
        tijd_voor_uit_en_instappen = pd.Timedelta(1, unit="minute")
        huidige_locatie_bus = omlopen[omloop_nr].iloc[omloop_laatste_rit_index]['eindlocatie']
        startlocatie_dienstregeling = dienstregeling.iloc[i]['startlocatie']
        
        # Controle of de bus op tijd en op de juiste locatie is
        if huidige_locatie_bus == startlocatie_dienstregeling and aankomsttijd_vorige_rit <= vertrektijd_dienstrit - tijd_voor_uit_en_instappen:
            omlopen[omloop_nr] = rit_toevoegen(omlopen[omloop_nr], dienstregeling.iloc[i], omloop_nr)
            dienstregeling = dienstregeling.drop(dienstregeling.index[i]).reset_index(drop=True)
            dienstritten_teller += 1
        else:
            i += 1
        
        # Controleer of we 11 dienstritten hebben toegevoegd
        if dienstritten_teller == 11:
            # Voeg materiaalritten en oplaadmoment toe
            omlopen[omloop_nr] = voeg_oplaad_momenten_toe(omlopen[omloop_nr], omloop_nr)
            dienstritten_teller = 0  # Reset de teller

    # Probeer enkele rit samen te voegen indien mogelijk
    merge_single_trip_if_possible(omlopen, omloop_nr)
    
    # Omloopnummer verhogen voor de volgende iteratie
    
    omloop_nr += 1


# Concateneer alle omlopen in één DataFrame
omloop_df = pd.concat([omlopen[i] for i in range(1, len(omlopen) + 1)], ignore_index=True)
omloop_df = voeg_materiaalritten_toe_aan_omlopen(omloop_df)

import acuucapaciteit as AC
omloop_df = AC.voeg_idle_tijden_toe(omloop_df)
omloop_df = AC.Afstand_omloop_toevoegen(omloop_df, afstandsmatrix)
omloop_df = AC.add_energy_usage_column(omloop_df)
omloop_df = AC.status(omloop_df, 300, 0.85)

omloop_df.to_excel("nieuwe_planning.xlsx", index=False)



"""
---------------------------------------------------------------------------------------------------------------------------------------
NU HEB JE EEN OMLOOPPLANNING DIE CORRECT IS "nieuwe_planning.xlxs", DEZE WORDT AANGEPAST (HANDMATIG) 
EN ONDER DE NIEUWE NAAM 'AANGEPAST_planning.xlsx' GEZET.
---------------------------------------------------------------------------------------------------------------------------------------
"""

# Lezen bestand
df = pd.read_excel('AANGEPAST_planning.xlsx')
# Drop de lege rijen
df = df.dropna(subset=['activiteit'])
# Reset de index
df = df.reset_index(drop=True)
# pas de start en eindtijden aan zodat deze overal hetzelfde zijn
df['starttijd'] = df['starttijd datum'].dt.time
df['eindtijd'] = df['eindtijd datum'].dt.time
# pas de kolom aan en visualiseer het 

df = CV.voeg_idle_tijden_toe(df)
df = CV.Afstand_omloop_toevoegen(df, afstandsmatrix)
df = CV.add_energy_usage_column(df)
df = CV.status(df, 300, 0.85)

CV.visualiseer_omloopplanning_met_oplaadmarkering(df)

df.to_excel("DE_PLANNING_handmatig.xlsx", index=False)
