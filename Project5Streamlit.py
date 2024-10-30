# streamlit run Project5Streamlit.py
import streamlit as st
import pandas as pd
import rit_haalbaar_binnen_tijd
import check_1_bus_per_rit
import VisualisatieOmloopplanning
import acuucapaciteit as AC
import DataframeCleaning
import io

# Inject custom CSS for button styling
def custom_button_css():
    st.markdown("""
        <style>
        /* General button style for primary outer buttons */
        .stButton > button {
            color: white;
            background-color: #673266; /* Purple */
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 8px;
            border: 2px solid #E6007E; /* Pinkish border */
        }
        .stButton > button:hover {
            background-color: #520050; /* Dark purple */
        }
        /* Inner button style for lighter pink */
        .stButton.light-pink > button {
            color: white;
            background-color: #E8A2C8; /* Light Pink */
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 8px;
            border: 1px solid #D081A1;
        }
        .stButton.light-pink > button:hover {
            background-color: #D081A1; /* Darker pink */
        }
        </style>
    """, unsafe_allow_html=True)


# Initialize session states for toggling sections
def initialize_states():
    if 'show_infeasible_trips' not in st.session_state:
        st.session_state.show_infeasible_trips = False
    if 'show_inaccuracies' not in st.session_state:
        st.session_state.show_inaccuracies = False
    if 'show_battery_status' not in st.session_state:
        st.session_state.show_battery_status = False
    if 'show_visualization' not in st.session_state:
        st.session_state.show_visualization = False
    if 'show_dataframe' not in st.session_state:
        st.session_state.show_dataframe = False
    if 'uploaded_omloopplanning' not in st.session_state:
        st.session_state.uploaded_omloopplanning = None
    if 'uploaded_dienstregeling' not in st.session_state:
        st.session_state.uploaded_dienstregeling = None

# Function for uploading Excel files
def file_upload_section():
    st.header("File Upload")
    omloopplanning_file = st.file_uploader("Choose the Excel file with the filled in **bus planning** (usually named something like \"omloopplanning.xlsx\")", type="xlsx")
    dienstregeling_file = st.file_uploader("Choose the Excel file with the **time table** (usually named something like \"Connection data 20##-20## .xlsx\")", type="xlsx")
    
    # Save files to session state
    if omloopplanning_file is not None:
        st.session_state.uploaded_omloopplanning = omloopplanning_file
    if dienstregeling_file is not None:
        st.session_state.uploaded_dienstregeling = dienstregeling_file

    # Display error messages if files are missing
    if dienstregeling_file is None:
        st.error("Error: No Excel file uploaded with the time table. Please upload a file like \"Connexxion data - 2024-2025.xlsx\", containing a sheet named \"Dienstregeling\" and \"Afstandsmatrix\" in the 'Import Data' section.")
    if omloopplanning_file is None:
        st.error("Error: No Excel file uploaded with the filled in bus planning. Please upload a file like \"omloopplanning.xlsx\" in the 'Import Data' section.")

# Display Infeasible Trips section
def display_infeasible_trips():
    if st.button("Check: Infeasible Trips"):
        st.session_state.show_infeasible_trips = not st.session_state.show_infeasible_trips

    if st.session_state.show_infeasible_trips:
        rit_haalbaar_binnen_tijd.inladen(
            pd.read_excel(st.session_state.uploaded_omloopplanning),
            pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix")
        )
        st.write("Infeasible trips:")
        df_niet_haalbaar = rit_haalbaar_binnen_tijd.niet_haalbare_ritten()
        df_niet_haalbaar = DataframeCleaning.omloopplanningEngels(df_niet_haalbaar)
        df_niet_haalbaar = DataframeCleaning.dienstregelingEngels(df_niet_haalbaar)
        st.dataframe(df_niet_haalbaar)
        st.write("This section displays the trips that are infeasible in the schedule. \nIf nothing is shown here, all trips are feasible.")
        st.markdown("---")

# Display Inaccuracies in Timetable section
def display_inaccuracies_in_timetable():
    if st.button("Check: Inaccuracies in Timetable"):
        st.session_state.show_inaccuracies = not st.session_state.show_inaccuracies

    if st.session_state.show_inaccuracies:
        check_1_bus_per_rit.inladen(
            pd.read_excel(st.session_state.uploaded_omloopplanning),
            pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix"),
            pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Dienstregeling")
        )
        st.write("Inaccuracies in the design of the timetable:")
        df_inaccuracies = check_1_bus_per_rit.niet_correcte_ritten()
        df_inaccuracies = DataframeCleaning.dienstregelingEngels(df_inaccuracies)
        st.dataframe(df_inaccuracies)
        st.write("These are trips from the timetable that: \n - are not assigned to any bus; \n - are assigned to multiple buses simultaneously.")
        st.markdown("---")

# Display Battery Status Visualization and DataFrame controls
def display_battery_status():
    # Main Battery Status button
    if st.button("Check: Battery Status"):
        st.session_state.show_battery_status = not st.session_state.show_battery_status
    if st.session_state.show_battery_status:
        st.write("The provided schedule has been adjusted; some idle trips have been removed, and some idle trips have been added.")
        selected_columns = [
            "Index", "startlocatie", "eindlocatie", "starttijd", "eindtijd", 
            "activiteit", "buslijn", "omloop nummer", "afstand in meters", 
            "energieverbruik nieuw", "Huidige energie", "Status"
        ]

        omloopplanning = pd.read_excel(st.session_state.uploaded_omloopplanning)
        connexxion_data = pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix")
        df = AC.voeg_idle_tijden_toe(omloopplanning)
        df = AC.detecteer_en_verwijder_foute_rijen(df)
        df = AC.Afstand_omloop_toevoegen(df, connexxion_data)
        df = AC.add_energy_usage_column(df, soh_value=0.85)
        df = AC.status(df, 300, 0.90, 0.10)

        # Inner "Show/Hide Visualization" button with lighter purple style
        st.markdown('<div class="stButton inner-button">', unsafe_allow_html=True)
        if st.button("Visualization", key="visualization_toggle", help="Click to show/hide the Gantt chart visualization"):
            st.session_state.show_visualization = not st.session_state.show_visualization
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.show_visualization:
            st.write("This visualization shows the trips that are not feasible (marked in red) because they fall below the minimum battery percentage.")
            visualisatie, _ = VisualisatieOmloopplanning.visualiseer_omloopplanning_met_oplaadmarkering(df)
            st.pyplot(visualisatie)

        # Inner "Show/Hide DataFrame" button with lighter purple style
        st.markdown('<div class="stButton inner-button">', unsafe_allow_html=True)
        if st.button("DataFrame with Battery Status", key="dataframe_toggle", help="Click to show/hide the DataFrame"):
            st.session_state.show_dataframe = not st.session_state.show_dataframe
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.show_dataframe:
            st.write("Adjusted DataFrame: \n - Afstand in meters: shows the distance of the trip \n - energieverbruik nieuw: shows the new calculated energy usage for the trip \n - Huidige energie: shows the current energy of the bus \n - Status: shows if the bus is above (OK) or below (Opladen Nodig) the minimum battery percentage")
            st.dataframe(df[selected_columns])

        # Button to download DataFrame as Excel
        st.markdown('<div class="stButton inner-button">', unsafe_allow_html=True)
        buffer = io.BytesIO()
        df[selected_columns].to_excel(buffer, index=False)
        st.download_button(
            label="Download DataFrame as Excel",
            data=buffer,
            file_name="battery_status_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button",
            help="Download the DataFrame as an Excel file",
        )

# Function to display uploaded files with toggling functionality
def raw_data_section():
    # Initialize the toggle state in session state if it doesn't exist
    if 'show_uploaded_files' not in st.session_state:
        st.session_state.show_uploaded_files = False

    # Toggle button for displaying uploaded files
    if st.button('Show/Hide Uploaded Files'):
        st.session_state.show_uploaded_files = not st.session_state.show_uploaded_files

    # Only display content if the toggle is on
    if st.session_state.show_uploaded_files:
        try: 
            # Load and display the bus planning file (omloopplanning)
            omloopplanning = DataframeCleaning.omloopplanningEngels(pd.read_excel(st.session_state.uploaded_omloopplanning))
            st.write("Here is the content of the uploaded bus planning file:")
            st.dataframe(omloopplanning)
        except:
            st.write("Please upload the bus planning file (usually named something like \"omloopplanning.xlsx\").")

        try: 
            # Load and display the time table (dienstregeling) and distance matrix (afstandsmatrix)
            dienstregeling = DataframeCleaning.dienstregelingEngels(pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Dienstregeling"))
            afstandsmatrix = DataframeCleaning.afstandsmatrixEngels(pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix"))

            st.write("Here is the content of the uploaded time table file.")
            st.write("Time table:")
            st.dataframe(dienstregeling)
            st.write("Distance matrix:")
            st.dataframe(afstandsmatrix)
        except:
            st.write("Please upload the time table file (usually named something like \"Connection data 20##-20## .xlsx\").")




# Main function
def main():
    custom_button_css()  # Activate custom button styles
    initialize_states()  # Initialize session states
    file_upload_section()  # File upload section

    # Only display buttons if both files are uploaded
    if st.session_state.uploaded_omloopplanning and st.session_state.uploaded_dienstregeling:
        st.markdown("---")
        raw_data_section() # Show uploaded files
        st.markdown("---")
        display_infeasible_trips()  # Show infeasible trips section
        display_inaccuracies_in_timetable()  # Show timetable inaccuracies section
        display_battery_status()  # Show battery status visualization and DataFrame controls

# Run the app
if __name__ == "__main__":
    main()