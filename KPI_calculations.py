import pandas as pd
import rit_haalbaar_binnen_tijd
import check_1_bus_per_rit

omloopplanning = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")

omloopplanning_nieuw = pd.read_excel("omloopplanning.xlsx")
afstandsmatrix_nieuw = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
dienstregeling_nieuw = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")


def aantal_bussen_vergelijken():
    aantal_bussen = omloopplanning['omloop nummer'].nunique()
    aantal_bussen_nieuw = omloopplanning_nieuw['omloop nummer'].nunique()
    KPI_aantal_bussen = aantal_bussen/aantal_bussen_nieuw
    return KPI_aantal_bussen





