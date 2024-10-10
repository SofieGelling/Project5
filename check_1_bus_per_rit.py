import pandas as pd

omloopplanning:pd.DataFrame  = None
afstandsmatrix:pd.DataFrame = None
dienstregeling:pd.DataFrame  = None

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

    # opvullen met nullen bij alle cellen waar geen buslijn nummer is ingevuld
    afstandsmatrix["buslijn"].fillna(0, inplace=True)
    omloopplanning["buslijn"].fillna(0, inplace=True)
    
    # ongeldige kolommen verwijderen
    omloopplanning.drop([229.5, 'Unnamed: 12', "originele accucapaciteit van 300kWu"], axis=1, inplace=True)

def aantal_bussen_ingepland_voor_rit(rit:pd.DataFrame)->int:
    aantal_bussen_voor_dienst = omloopplanning[(omloopplanning["startlocatie"] == rit["startlocatie"])
                                               & (omloopplanning["eindlocatie"] == rit["eindlocatie"])
                                               & (pd.Series(omloopplanning["starttijd"].str[:-3]) == rit["vertrektijd"])
                                               & (omloopplanning["buslijn"] == rit["buslijn"])
                                               ]
    return len(aantal_bussen_voor_dienst)


if __name__ == "__main__":
    initialisatie()
    # handmatig geïntroduceerde fout om te testen: 
    # dienstregeling.iat[1,1] = "06:05"
    dienstregeling["aantal bussen die deze rit rijdt"] = dienstregeling.apply(aantal_bussen_ingepland_voor_rit, axis=1)
    print("de dienstregeling data: ")
    print(dienstregeling)

    print("correcte ritten (ritten uit de dienstregelingen die door 1 bus gereden worden )")
    print(dienstregeling[dienstregeling["aantal bussen die deze rit rijdt"] == 1])

    print("foute ritten (ritten uit de dienstregelingen die door 0 of meerdere bussen gereden worden): ")
    print(dienstregeling[dienstregeling["aantal bussen die deze rit rijdt"] != 1])