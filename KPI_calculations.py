import pandas as pd

omloopplanning = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")

omloopplanning_nieuw = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix_nieuw = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling_nieuw = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")


def verschil_aantal_bussen(bus_schedule, bus_schedule_new):
    aantal_bussen = bus_schedule['omloop nummer'].nunique()
    aantal_bussen_nieuw = bus_schedule_new['omloop nummer'].nunique()
    verschil = aantal_bussen_nieuw - aantal_bussen
    return verschil

def verschil_materiaal_ritten(bus_schedule, bus_schedule_new):
    aantal_materiaal_ritten = bus_schedule['activiteit'][bus_schedule['activiteit'] == 'materiaal rit'].count()
    aantal_materiaal_ritten_nieuw = bus_schedule_new['activiteit'][bus_schedule_new['activiteit'] == 'materiaal rit'].count()
    verschil = aantal_materiaal_ritten_nieuw - aantal_materiaal_ritten
    return verschil

def verschil_tijd_materiaal_ritten(bus_schedule, bus_schedule_new):
    materiaal_ritten = bus_schedule[bus_schedule['activiteit'] == 'materiaal rit']
    materiaal_ritten_nieuw = bus_schedule_new[bus_schedule_new['activiteit'] == 'materiaal rit']
    materiaal_ritten['tijd_minuten'] = (materiaal_ritten['eindtijd datum'] - materiaal_ritten['starttijd datum']).dt.total_seconds() / 60
    materiaal_ritten_nieuw['tijd_minuten'] = (materiaal_ritten_nieuw['eindtijd datum'] - materiaal_ritten_nieuw['starttijd datum']).dt.total_seconds() / 60
    verschil = materiaal_ritten_nieuw['tijd_minuten'].sum() - materiaal_ritten['tijd_minuten'].sum()
    return verschil

