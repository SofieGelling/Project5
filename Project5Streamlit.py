# streamlit run Project5Streamlit.py
import streamlit as st
import pandas as pd

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
    if st.button('Import data'):
        # Toggle the visibility of the file uploader
        st.session_state.show_uploader = not st.session_state.show_uploader

    # Show file uploader if the state is True
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

        # Check if a file has been uploaded
        if uploaded_file is not None:
            # Read the uploaded Excel file using pandas
            df = pd.read_excel(uploaded_file)

            # Display the DataFrame
            st.write("Here is the content of the uploaded Excel file:")
            st.dataframe(df)
        else:
            st.write("Please upload an Excel file.")

# Main part of the script
def main():
    # Activate custom button
    custom_button_css()

    # Initialize states
    initialize_states()

    # Product info section
    software_tool_information()

    # Add a separator between the sections
    st.markdown("---")

    # Additional info section
    results()

    # Add a separator between the sections
    st.markdown("---")

    # File upload section
    file_upload_section()

# Run the app
if __name__ == "__main__":
    main()




