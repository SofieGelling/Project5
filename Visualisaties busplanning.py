import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates

# Load the data from the Excel file
file_path = 'omloopplanning.xlsx'
data_df = pd.read_excel(file_path)

# Convert 'starttijd datum' and 'eindtijd datum' columns from string to datetime format
data_df['starttijd datum'] = pd.to_datetime(data_df['starttijd datum'], errors='coerce')  # Convert and handle errors
data_df['eindtijd datum'] = pd.to_datetime(data_df['eindtijd datum'], errors='coerce')

# Remove rows where 'starttijd datum' or 'eindtijd datum' could not be converted
data_df = data_df.dropna(subset=['starttijd datum', 'eindtijd datum'])

# Prepare the data
omloop_nummers = data_df['omloop nummer'].unique()  # Get unique 'omloop nummer'
omloop_mapping = {omloop: i for i, omloop in enumerate(omloop_nummers)}  # Map each 'omloop nummer' to a number for the y-axis

# Specify the desired colors for each activity
color_mapping = {
    'materiaal rit': 'orange',
    'dienst rit': 'green',
    'opladen': 'blue',
    'idle': 'gray'
}

# Create the plot
fig, ax = plt.subplots(figsize=(12, 8))

# Plot each 'omloop nummer' schedule as horizontal bars
for _, row in data_df.iterrows():
    omloop = row['omloop nummer']
    activity = row['activiteit']
    start_time = row['starttijd datum']
    end_time = row['eindtijd datum']
    
    # Calculate the duration in days (since matplotlib handles time as days)
    duration = (end_time - start_time).total_seconds() / (24 * 3600)  # Duration in days

    # Add a horizontal bar for each 'activiteit', using the start time and duration
    ax.barh(omloop_mapping[omloop], duration, left=mdates.date2num(start_time), 
            color=color_mapping.get(activity, 'black'), edgecolor='black')  # Use 'black' as default color if activity is missing

# Set the x-axis to display times in Date and HH:MM format
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

# Set x-axis limits to cover exactly one day starting from the earliest start time minus 1 hour
start_limit = data_df['starttijd datum'].min() - pd.Timedelta(hours=1)  # Subtract 1 hour for padding
ax.set_xlim([mdates.date2num(start_limit), mdates.date2num(start_limit + pd.Timedelta(days=1))])

# Add labels, legend, and title
ax.set_yticks(list(omloop_mapping.values()))  # Set y-ticks as omloop nummers
ax.set_yticklabels(omloop_nummers)  # Map the y-tick labels to 'omloop nummer'
ax.set_xlabel('Time')
ax.set_ylabel('Omloop Nummer')
ax.set_title('Omloop Planning with Activities Over Time')

# Create legend for activities
handles = [mpatches.Patch(color=color_mapping[act], label=act) for act in color_mapping]
ax.legend(handles=handles, title='Activiteit')

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
