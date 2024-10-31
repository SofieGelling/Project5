import pandas as pd

omloopplanning = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")

def omloopplanningEngels(bus_schedule):
    result = bus_schedule.copy()
    result = result.drop('Unnamed: 0', axis=1) #zodat de index niet dubbel wordt laten zien in de tool
    result = result.rename(columns={'startlocatie': 'Start Location', 'eindlocatie': 'End Location', 'starttijd': 'Start Time', 'eindtijd': 'End Time', 'activiteit': 'Activity', 'buslijn': 'Bus Line', 'energieverbruik': 'Energy consumption', 'starttijd datum': 'Start Time Date', 'eindtijd datum': 'End Time Date', 'omloop nummer': 'Bus Number', 'afstand in meters': 'disctance in meters', 'Huidige energie': 'current energy'})
    return result

def omloopplanning_vertalen(bus_schedule):
    result = bus_schedule.copy()
    result = result.rename(columns={'startlocatie': 'Start Location', 'eindlocatie': 'End Location', 'starttijd': 'Start Time', 'eindtijd': 'End Time', 'activiteit': 'Activity', 'buslijn': 'Bus Line', 'energieverbruik': 'Energy consumption', 'starttijd datum': 'Start Time Date', 'eindtijd datum': 'End Time Date', 'omloop nummer': 'Bus Number', 'afstand in meters': 'Disctance in meters', 'Huidige energie': 'Current energy', 'energieverbruik nieuw': 'Energy consumption'})
    return result

def afstandsmatrixEngels(distance_matrix):
    result = distance_matrix.copy()
    result = result.rename(columns={'startlocatie': 'Start Location','eindlocatie': 'End Location','min reistijd in min': 'Min Travel Time (min)','max reistijd in min': 'Max Travel Time (min)','afstand in meters': 'Distance (m)','buslijn': 'Bus Line'})
    return result

def dienstregelingEngels(bus_timetable):
    result = bus_timetable.copy()
    result = result.rename(columns={'startlocatie':'Start Location', 'vertrektijd':'Departure Time', 'eindlocatie': 'End Location', 'buslijn':'Bus Line'})
    return result
