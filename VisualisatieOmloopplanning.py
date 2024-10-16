import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

# Pad naar het Excel-bestand
file_path = 'omloopplanning.xlsx'

def Visualiatie(Gelezen_document):
    # Laad het bestand en verwijder extra spaties uit kolomnamen
    #df = pd.read_excel(file_path)
    #print(df.head(10))
    df = Gelezen_document
    df.columns = df.columns.str.strip()  # Verwijder onzichtbare spaties rondom de kolomnamen

    # Zet start- en eindtijden om naar datetime voor plotten
    df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
    df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])

    # Kleurmapping voor de verschillende activiteiten
    color_map = {
        ('dienst rit', 'ehvapt', 'ehvbst'): '#4682B4',    # dienst rit heenrit (darker blue)
        ('dienst rit', 'ehvbst', 'ehvapt'): '#6495ED',    # dienst rit terugrit (lighter blue)
        ('materiaal rit', 'ehvapt', 'ehvbst'): '#EE1289', # materiaal rit eindigt bij ehvbst (red)
        ('materiaal rit', 'ehvbst', 'ehvapt'): '#FF3E96', # materiaal rit eindigt bij ehvapt (light red)
        'idle': 'lightgrey',                              # idle (light grey)
        'opladen': '#00EE00',                             # opladen (green)
        'unmapped': '#C1FFC1'                             # materiaalrit naar oplaadpunt (light green)
    }

    # Begin met plotten
    fig, ax = plt.subplots(figsize=(12, 8))
    y_labels = []
    y_pos = 0  # Verticale positie voor elke unieke omloop

    # Voor elke unieke omloop plotten we de activiteiten
    for run in df['omloop nummer'].unique():
        run_data = df[df['omloop nummer'] == run]
        y_labels.append(f'Run {int(run)}')
        for _, row in run_data.iterrows():
            # Kies kleur op basis van activiteit en route, gebruik 'unmapped' als fallback
            color = color_map.get((row['activiteit'], row['startlocatie'], row['eindlocatie']), 
                                color_map.get(row['activiteit'], color_map['unmapped']))
            
            # Teken een balk voor de duur van de activiteit
            ax.barh(y_pos, row['eindtijd datum'] - row['starttijd datum'], left=row['starttijd datum'], color=color)
        
        # Verhoog de verticale positie voor de volgende omloop
        y_pos += 1

    # Stel labels en as-instellingen in
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Time")
    ax.set_ylabel("Runs")

    # Legenda voor de kleuren
    legend_elements = [
        Patch(facecolor='#4682B4', label='dienst rit ehvapt -> ehvbst (heenrit)'),
        Patch(facecolor='#6495ED', label='dienst rit ehvbst -> ehvapt (terugrit)'),
        Patch(facecolor='#EE1289', label='materiaal rit ehvapt -> ehvbst'),
        Patch(facecolor='#FF3E96', label='materiaal rit ehvbst -> ehvapt'),
        Patch(facecolor='lightgrey', label='idle'),
        Patch(facecolor='#00EE00', label='opladen'),
        Patch(facecolor='#C1FFC1', label='materiaalrit naar garage')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Formatteer de x-as om tijd weer te geven
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Laat de titel en rasterinstellingen zien
    plt.title("Omloopplanning Gantt Chart")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def Visualiatie_met_busnummers(file_path):
    df = file_path
    df.columns = df.columns.str.strip()  # Verwijder onzichtbare spaties rondom de kolomnamen

    # Zet start- en eindtijden om naar datetime voor plotten
    df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
    df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])

    # Kleurmapping voor de verschillende activiteiten
    color_map = {
        ('dienst rit', 'ehvapt', 'ehvbst'): '#4682B4',    # dienst rit heenrit (darker blue)
        ('dienst rit', 'ehvbst', 'ehvapt'): '#6495ED',    # dienst rit terugrit (lighter blue)
        ('materiaal rit', 'ehvapt', 'ehvbst'): '#EE1289', # materiaal rit eindigt bij ehvbst (red)
        ('materiaal rit', 'ehvbst', 'ehvapt'): '#FF3E96', # materiaal rit eindigt bij ehvapt (light red)
        'idle': 'lightgrey',                              # idle (light grey)
        'opladen': '#00EE00',                             # opladen (green)
        'unmapped': '#C1FFC1'                             # materiaalrit naar oplaadpunt (light green)
    }

    # Begin met plotten
    fig, ax = plt.subplots(figsize=(12, 8))
    y_labels = []
    y_pos = 0  # Verticale positie voor elke unieke omloop

    # Voor elke unieke omloop plotten we de activiteiten
    for run in df['omloop nummer'].unique():
        run_data = df[df['omloop nummer'] == run]
        y_labels.append(f'Run {int(run)}')
        for _, row in run_data.iterrows():
            # Kies kleur op basis van activiteit en route, gebruik 'unmapped' als fallback
            color = color_map.get((row['activiteit'], row['startlocatie'], row['eindlocatie']), 
                                color_map.get(row['activiteit'], color_map['unmapped']))
            
            # Teken een balk voor de duur van de activiteit
            ax.barh(y_pos, row['eindtijd datum'] - row['starttijd datum'], left=row['starttijd datum'], color=color)
            
            # Voeg busnummer (buslijn) toe binnen de vakken als aanwezig
            if not pd.isna(row['buslijn']):
                ax.text(row['starttijd datum'] + (row['eindtijd datum'] - row['starttijd datum']) / 2,
                        y_pos, str(int(row['buslijn'])), ha='center', va='center', color='white', fontsize=8)
        
        # Verhoog de verticale positie voor de volgende omloop
        y_pos += 1

    # Stel labels en as-instellingen in
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("Time")
    ax.set_ylabel("Runs")

    # Legenda voor de kleuren
    legend_elements = [
        Patch(facecolor='#4682B4', label='dienst rit ehvapt -> ehvbst (heenrit)'),
        Patch(facecolor='#6495ED', label='dienst rit ehvbst -> ehvapt (terugrit)'),
        Patch(facecolor='#EE1289', label='materiaal rit ehvapt -> ehvbst'),
        Patch(facecolor='#FF3E96', label='materiaal rit ehvbst -> ehvapt'),
        Patch(facecolor='lightgrey', label='idle'),
        Patch(facecolor='#00EE00', label='opladen'),
        Patch(facecolor='#C1FFC1', label='materiaalrit naar garage')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Formatteer de x-as om tijd weer te geven
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Laat de titel en rasterinstellingen zien
    plt.title("Omloopplanning Gantt Chart met Busnummers")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()




