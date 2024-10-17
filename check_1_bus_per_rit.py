import pandas as pd

omloopplanning:pd.DataFrame  = None
afstandsmatrix:pd.DataFrame = None
dienstregeling:pd.DataFrame  = None
data_opgeschoond = False
correctheid_berekend = False

def initialisatie()->None:
    """Excelbestanden inladen en data klaar maken voor gebruik
    """
    # inladen excelsheets
    global omloopplanning
    global afstandsmatrix
    global dienstregeling
    omloopplanning = pd.read_excel("omloopplanning.xlsx")
    afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix")
    dienstregeling = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling")
    data_opschonen()
    
def inladen(nieuwe_omloopplanning, nieuwe_afstandsmatrix, nieuwe_dienstregeling):
    global omloopplanning
    global afstandsmatrix
    global dienstregeling
    global data_opgeschoond
    global correctheid_berekend
    omloopplanning = nieuwe_omloopplanning
    afstandsmatrix = nieuwe_afstandsmatrix
    dienstregeling = nieuwe_dienstregeling
    data_opgeschoond = False
    correctheid_berekend = False
    data_opschonen()
    kolommen_toevoegen_aantal_bussen()
    
def data_opschonen():
    global data_opgeschoond
    # opvullen met nullen bij alle cellen waar geen buslijn nummer is ingevuld
    afstandsmatrix["buslijn"].fillna(0, inplace=True)
    omloopplanning["buslijn"].fillna(0, inplace=True)
    
    # ongeldige kolommen verwijderen
    try:
        omloopplanning.drop([229.5, 'Unnamed: 12', "originele accucapaciteit van 300kWu"], axis=1, inplace=True)
    except:
        pass
    data_opgeschoond = True
    

def aantal_bussen_ingepland_voor_rit(rit:pd.DataFrame)->int:
    aantal_bussen_voor_dienst = omloopplanning[(omloopplanning["startlocatie"] == rit["startlocatie"])
                                               & (omloopplanning["eindlocatie"] == rit["eindlocatie"])
                                               & (pd.Series(omloopplanning["starttijd"].str[:-3]) == rit["vertrektijd"])
                                               & (omloopplanning["buslijn"] == rit["buslijn"])
                                               ]
    return len(aantal_bussen_voor_dienst)

def kolommen_toevoegen_aantal_bussen():
    global correctheid_berekend
    dienstregeling.iat[1,1] = "06:05"
    dienstregeling["aantal bussen die deze rit rijdt"] = dienstregeling.apply(aantal_bussen_ingepland_voor_rit, axis=1)
    correctheid_berekend = True

def correcte_ritten():
    if data_opgeschoond == False:
        data_opschonen()
    if correctheid_berekend == False:
        kolommen_toevoegen_aantal_bussen()
    return dienstregeling[dienstregeling["aantal bussen die deze rit rijdt"] == 1]
    
def niet_correcte_ritten():
    if data_opgeschoond == False:
        data_opschonen()
    if correctheid_berekend == False:
        kolommen_toevoegen_aantal_bussen()
    return dienstregeling[dienstregeling["aantal bussen die deze rit rijdt"] != 1]

if __name__ == "__main__":
    initialisatie()
    #inladen(pd.read_excel("omloopplanning.xlsx"), pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Afstandsmatrix"), pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name="Dienstregeling"))
    # handmatig geïntroduceerde fout om te testen: 
    # dienstregeling.iat[1,1] = "06:05"
    print("de dienstregeling data: ")
    print(dienstregeling)
    print("correcte ritten (ritten uit de dienstregelingen die door 1 bus gereden worden )")
    print(correcte_ritten())

    print("foute ritten (ritten uit de dienstregelingen die door 0 of meerdere bussen gereden worden): ")
    print(niet_correcte_ritten())