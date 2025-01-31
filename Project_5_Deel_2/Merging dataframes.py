import pandas as pd
 
# Paths to the Excel files

filtered_data_path = 'filtered_data.xlsx'

degree_data_path = 'degree.xlsx'
 
# Load the Excel files

filtered_data = pd.read_excel(filtered_data_path)

degree_data = pd.read_excel(degree_data_path)
 
# Select the last three columns from the degree data

degree_last_three_columns = degree_data.iloc[:, -3:]
 
# Add the "t" column for merging purposes

degree_last_three_columns['t'] = degree_data['t']
 
# Merge the dataframes on the "t" column

merged_data = pd.merge(filtered_data, degree_last_three_columns, on='t', how='inner')
 
# Save the merged data to a new file

merged_data.to_excel('merged_data.xlsx', index=False)

 