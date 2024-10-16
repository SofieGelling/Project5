# streamlit run Project5Streamlit_alles_lekker_leeg.py
import streamlit as st
import pandas as pd
import rit_haalbaar_binnen_tijd
import check_1_bus_per_rit

# Inject custom CSS for button styling
def custom_button_css():
    st.markdown("""
        <style>
        /* General button style */
        .stButton > button {
            color: white;
            background-color: #673266; /* Purple */
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 8px;
            border: 2px solid #E6007E; /* Pinkish border */
        }

        /* Hover effect - should change to a darker purple */
        .stButton > button:hover {
            background-color: #520050; /* Dark purple */
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize the state for toggling product info, additional info, and file uploader
def initialize_states():
    if 'show_info' not in st.session_state:
        st.session_state.show_info = False
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'show_uploader' not in st.session_state:
        st.session_state.show_uploader = False
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'uploaded_omloopplanning' not in st.session_state:
        st.session_state.uploaded_omloopplanning = None
    if 'uploaded_dienstregeling' not in st.session_state:
        st.session_state.uploaded_dienstregeling = None

# Function for software tool information section
def software_tool_information():
    st.header("Software tool Information")
    if st.button('Show/Hide Info'):
        st.session_state.show_info = not st.session_state.show_info

    # Conditionally display or hide the information
    if st.session_state.show_info:
        st.info("**Software tool Information**\n- Description\n- Usage\n- Data type\n- Output")

# Function for results section
def results():
    st.header("Results")
    if st.button('Show/Hide Results'):
        st.session_state.show_results = not st.session_state.show_results

    # Conditionally display or hide results
    if st.session_state.show_results:
        st.info("**Planning**\n\n ...")

# Function for uploading Excel files
def file_upload_section():
    st.header("File Upload")
    omloopplanning_file = st.file_uploader("Choose the Excel file with the **omloopplanning**", type="xlsx")
    dienstregeling_file = st.file_uploader("Choose the Excel file with the **dienstregeling** (usually named something like \"Connection data 20##-20## .xlsx\")", type="xlsx")
    
    # Check if a file has been uploaded
    if omloopplanning_file is not None:
        st.session_state.uploaded_omloopplanning = omloopplanning_file  # Save the file to session state

    # Check if a file has been uploaded
    if dienstregeling_file is not None:
        st.session_state.uploaded_dienstregeling = dienstregeling_file  # Save the file to session state

    if dienstregeling_file is not None and omloopplanning_file is not None:
        if st.session_state.uploaded_omloopplanning is None:
            st.error("Error: No Excel file with omloopplanning uploaded. Please upload a file like \"omloopplanning.xlsx\" in the 'Import Data' section.")
        
        if st.session_state.uploaded_dienstregeling is None:
            st.error("Error: No Excel file with dienstregeling uploaded. Please upload a file like \"Connexxion data - 2024-2025.xlsx\", containing a sheet named \"Dienstregeling\" and \"Afstandsmatrix\" in the 'Import Data' section.")
        
        if not (st.session_state.uploaded_omloopplanning is None) and not (st.session_state.uploaded_dienstregeling is None):
            # put the dataframes from excel files in module rit_haalbaar_binnen_tijd
            rit_haalbaar_binnen_tijd.omloopplanning = pd.read_excel(st.session_state.uploaded_omloopplanning)
            rit_haalbaar_binnen_tijd.afstandsmatrix = pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix")
            
            # output haalbaarheid
            st.write("Niet haalbare ritten: ")
            st.dataframe(rit_haalbaar_binnen_tijd.niet_haalbare_ritten())
            
            # put the dataframes from excel files in module rit_haalbaar_binnen_tijd
            check_1_bus_per_rit.omloopplanning = pd.read_excel(st.session_state.uploaded_omloopplanning)
            check_1_bus_per_rit.dienstregeling = pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Dienstregeling")
            check_1_bus_per_rit.afstandsmatrix = pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix")
            
            # output dienstregeling juist ingevuld
            st.write("Onjuistheden in de invulling van de dienstregeling.")
            st.write("Alle ritten uit de dienstregelingen die door 0 of meerdere bussen gereden worden:")
            st.dataframe(check_1_bus_per_rit.niet_correcte_ritten())

# Function to run a piece of code when button is clicked, but checks for file first
def run_code_button():
    if st.button('Show/Hide Raw Data'):
        omloopplanning = pd.read_excel(st.session_state.uploaded_omloopplanning)
        dienstregeling = pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Dienstregeling")
        afstandsmatrix = pd.read_excel(st.session_state.uploaded_dienstregeling, sheet_name="Afstandsmatrix")
        
        # Display the DataFrames
        st.write("Here is the content of the uploaded omloopplanning file:")
        st.dataframe(omloopplanning)
        st.write("Here is the content of the uploaded dienstregeling file.")
        st.write("Dienstregeling:")    
        st.dataframe(dienstregeling)
        st.write("Afstandsmatrix:")
        st.dataframe(afstandsmatrix)
    

# Main part of the script
def main():
    # Activate custom button
    custom_button_css()

    # Initialize states
    initialize_states()

    # # Product info section
    # software_tool_information()
    #
    # # Add a separator between the sections
    # st.markdown("---")

    # File upload section
    file_upload_section()

    # Add a separator between the sections
    st.markdown("---")

    run_code_button()

    # # Add a separator between the sections
    # st.markdown("---")

    # # Additional info section
    # results()

# Run the app
if __name__ == "__main__":
    main()





