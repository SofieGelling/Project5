import pandas as pd
import datetime as dt

omloopplanning = None
afstandsmatrix = None
data_opgeschoond = False
haalbaarheid_berekend = False

def initialisatie()->None:
    """Excelbestanden inladen en data klaar maken voor gebruik
    """
    # inladen excelsheets
    global omloopplanning
    global afstandsmatrix
    omloopplanning = pd.read_excel("omloopplanning.xlsx")
    afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
    data_opschonen()

def data_opschonen():
    global data_opgeschoond
    # opvullen met nullen bij alle cellen waar geen buslijn nummer is ingevuld
    print(f"afstandsmatrix: {afstandsmatrix}")
    afstandsmatrix["buslijn"].fillna(0, inplace=True)
    omloopplanning["buslijn"].fillna(0, inplace=True)
    
    # ongeldige kolommen verwijderen
    try:
        omloopplanning.drop([229.5, 'Unnamed: 12', "originele accucapaciteit van 300kWu"], axis=1, inplace=True)
    except:
        pass
    data_opgeschoond = True
    
def inladen(nieuwe_omloopplanning, nieuwe_afstandsmatrix):
    global omloopplanning
    global afstandsmatrix
    global data_opgeschoond
    global correctheid_berekend
    omloopplanning = nieuwe_omloopplanning
    afstandsmatrix = nieuwe_afstandsmatrix
    data_opgeschoond = False
    correctheid_berekend = False
    data_opschonen()
    kolommen_toevoegen_haalbaarheid()

## extra controle: print alle rijen waar de tijd in de kolommen "starttijd" en "starttijd datum" niet overeenkomen.
# print(omloopplanning[omloopplanning[["starttijd", "starttijd datum"]].apply((lambda x: not str(x["starttijd datum"]).endswith(str(x["starttijd"]))), axis=1)])

# Berekent of de geplande ritduur niet te kort is voor een gegeven rit (rij in omloopplanning.xlsx).
def rit_haalbaar_binnen_de_tijd(rit:pd.DataFrame)->bool:
    """Of de geplande ritduur lang genoeg volgens de tijden in de  afstandsmatrix sheet.

    Args:
        rit (pd.DataFrame): rij in omloopplanning.xlsx met starttijd, eindtijd, start- en eindlocatie.

    Returns:
        (bool): of de geplande tijdsduur voor deze rit lang genoeg is
    """
    gr = geplande_reistijd(rit)
    kmr = kortst_mogelijke_reistijd_voor_rit(rit)
    haalbaar = gr >= kmr
    return haalbaar

def geplande_reistijd(rit:pd.DataFrame)->float:
    """ De geplande ritduur voor een gegeven rit, in seconden.
    Args: 
        rit (pd.DataFrame):  een rij uit omloopplanning.xlsx
        
    Returns:
        (float):  hoelang de rit duurt volgens de omloopplanning, in seconden.
    """
    tijd_gepland = pd.to_datetime(rit["eindtijd datum"]) - pd.to_datetime(rit["starttijd datum"])
    return tijd_gepland.total_seconds()

def kortst_mogelijke_reistijd_voor_rit(rit:pd.DataFrame)->float:
    """De tijd die op zijn minst nodig is voor een gegeven rit, volgens de afstandsmatrix sheet in "Connexxion data ~~~.xlsx" , in seconden.
    Args:
        rit (pd.DataFrame): een rij uit omloopplanning.xlsx
        
    Returns:
        (float): tijd nodig voor rit in seconden.
    """
    startlocatie = rit["startlocatie"]
    eindlocatie = rit["eindlocatie"]
    min_reistijd = 0
    if startlocatie == eindlocatie:
        min_reistijd = pd.to_timedelta(dt.timedelta(minutes=0))
    else: 
        rit_uit_afstandsmatrix = afstandsmatrix[(startlocatie == afstandsmatrix["startlocatie"]) 
                                                & (eindlocatie == afstandsmatrix["eindlocatie"]) 
                                                & (rit["buslijn"] == afstandsmatrix["buslijn"])
                                                ]
        min_reistijd = pd.to_timedelta(dt.timedelta(minutes = int(rit_uit_afstandsmatrix["min reistijd in min"].iat[0])))
    return min_reistijd.total_seconds()

def kolommen_toevoegen_haalbaarheid():
    omloopplanning["Trip duration as planned"] = omloopplanning.apply(geplande_reistijd, axis = 1)
    omloopplanning["Shortest possible trip duration"] = omloopplanning.apply(kortst_mogelijke_reistijd_voor_rit, axis = 1)
    omloopplanning["Trip feasible within time"] = omloopplanning.apply(rit_haalbaar_binnen_de_tijd, axis = 1)
    global haalbaarheid_berekend
    haalbaarheid_berekend = True
    
def haalbare_ritten():
    if data_opgeschoond == False:
        data_opschonen()
    if haalbaarheid_berekend == False:
        kolommen_toevoegen_haalbaarheid()
    return omloopplanning[omloopplanning["Trip feasible within time"]]
    
def niet_haalbare_ritten():
    if data_opgeschoond == False:
        data_opschonen()
    if haalbaarheid_berekend == False:
        kolommen_toevoegen_haalbaarheid()
    return omloopplanning[~omloopplanning["Trip feasible within time"]]

if __name__ == "__main__":
    initialisatie()
    # inladen(pd.read_excel("omloopplanning.xlsx"), pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix"))
    
    omloopplanning.columns
    print("~~~~~~~~~ Ritten haalbaar binnen de tijd: ")
    print(haalbare_ritten())
    print("~~~~~~~~~ Niet haalbare ritten: ")
    print(niet_haalbare_ritten())