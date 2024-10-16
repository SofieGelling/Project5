import pandas as pd

omloopplanning = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")

omloopplanning_nieuw = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix_nieuw = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling_nieuw = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")


def verschil_aantal_bussen():
    aantal_bussen = omloopplanning['omloop nummer'].nunique()
    aantal_bussen_nieuw = omloopplanning_nieuw['omloop nummer'].nunique()
    verschil = aantal_bussen_nieuw - aantal_bussen
    return verschil

def verschil_materiaal_ritten():
    aantal_materiaal_ritten = omloopplanning['activiteit'][omloopplanning['activiteit'] == 'materiaal rit'].count()
    aantal_materiaal_ritten_nieuw = omloopplanning_nieuw['activiteit'][omloopplanning_nieuw['activiteit'] == 'materiaal rit'].count()
    verschil = aantal_materiaal_ritten_nieuw - aantal_materiaal_ritten
    return verschil

def verschil_tijd_materiaal_ritten():
    materiaal_ritten = omloopplanning[omloopplanning['activiteit'] == 'materiaal rit']
    materiaal_ritten_nieuw = omloopplanning_nieuw[omloopplanning_nieuw['activiteit'] == 'materiaal rit']
    materiaal_ritten['tijd_minuten'] = (materiaal_ritten['eindtijd datum'] - materiaal_ritten['starttijd datum']).dt.total_seconds() / 60
    materiaal_ritten_nieuw['tijd_minuten'] = (materiaal_ritten_nieuw['eindtijd datum'] - materiaal_ritten_nieuw['starttijd datum']).dt.total_seconds() / 60
    verschil = materiaal_ritten_nieuw['tijd_minuten'].sum() - materiaal_ritten['tijd_minuten'].sum()
    return verschil

