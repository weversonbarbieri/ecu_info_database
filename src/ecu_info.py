import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import db
import json
import datetime
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(
     # Shows the page title
    page_title="ECU DataBase",
    # Shows the page icon on the browser tab.
    page_icon=":computer:",
    layout='centered',
    initial_sidebar_state='expanded'
)

# URL of the app image
url_app_image = "https://raw.githubusercontent.com/weversonbarbieri/ecu_info_database/master/image/app_image.jpg"

# Request the app image from the URL
response_app_image = requests.get(url_app_image)

# Open the image content
content_image_app = Image.open(BytesIO(response_app_image.content))

# Resize the image
image_app_resized = content_image_app.resize((1000, 250))

# Display the image in the Streamlit app
st.image(image_app_resized)

# Write the app's title in HMTL.
st.write("<div align='Center'><h2><i>Diagnostic Assistant Database</i></h2></div>", unsafe_allow_html=True)


# Load the secret key from Streamlit secrets
key_dict = json.loads(st.secrets["json_key"])

# Initialize Firebase
if not firebase_admin._apps: 
    # Create a credential object using the secret key
    cred = credentials.Certificate(key_dict)
    # Initialize the Firebase app with the credential
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

@st.cache_data
# Function to add text to Firestore
def add_text(issue, information):
    # Reference to the document in the Firestore collection
    doc_ref = db.collection(make_input).document(subject)
    # Stores the input's timestamp
    time_info = datetime.datetime.now()
    # Set the data in the document
    doc_ref.set({
            'Technician': {technician},
            'Date': {time_info},
            'Issue': {issue},
            'Information': {information}
            }
            )


# Create two tabs in the Streamlit app
tab1, tab2, tab3 = st.tabs(["Enter Information", "Information", "Update Information"])

with tab1:

    # Options for the 'Technician' dropdown menu
    technicians_list = ["Adeosun", "Martin", "Tavassika", "Weverson"]
    # Create a selectbox for 'Technician' options
    technician = st.selectbox("Technician:", technicians_list)

    # Create a selectbox for 'Make' options
    make_input = st.text_input('Enter the Make:')

    # Create a selectbox for document options
    subject = st.text_input('Enter the Subject (ENTER THE INFO IN CAPS LETTERS):')

    # Create a text input for 'Issue'
    issue = st.text_input("Enter the Issue:", key='issue_input')

    # Create a text area for 'Information'
    information = st.text_area('Enter the resolution/information')

    # Button to save the text
    if st.button('Save Text'):
        # Call the function to add text to Firestore
        add_text(issue, information)
        # Display a success message
        message_info_added = st.success(f'Information added successfully!')
        if message_info_added == 'Information added successfully!':
            add_text(issue, information)

with tab2:
    # Function to get the collection list
    def get_collection_list():
        collections = db.collections()
        collection_list = []
        # Append the collection IDs to the list
        for collection in collections:
            collection_list.append(collection.id)
        return collection_list

    # Function to get the document list
    def get_doc_list(make_name):
        subjects_ref = db.collection(make_name)
        # Get the documents in the collection
        subjects = subjects_ref.get()
        # Create a list to store the document IDs
        subject_list = []
        for sub in subjects:
            # Append the document IDs to the list
            subject_list.append(sub.id)
        return subject_list
    
    # Function to get the field list
    def get_field_list(make_given, subject_given):
        information = db.collection(make_given).document(subject_given)   
        info_ref = information.get()
        # Convert the document to a dictionary
        info_to_dict = info_ref.to_dict()
        # Create a list to store the fields
        fields_list = []
        # Loop to get the fields
        for fields in info_to_dict:
                # Exclude the 'Date' and 'Technician' fields 
                if fields != "Date" and fields != "Technician":
                    # Append the fields to the list
                    fields_list.append(fields) 
        return fields_list
    
    # Function to show the information from each field stored in Firestore
    def show_information_resolution(make_given, subject_given, field):
        # Reference to the document in Firestore
        information = db.collection(make_given).document(subject_given)
        # Get the information from the document
        info_ref = information.get()
        # Covert the information to a dictionary
        info_to_dict = info_ref.to_dict()
        # Get the information from each field
        info_to_show = info_to_dict.get(field, "")
        return info_to_show
    
    # Create a selectbox for 'Make' options
    make_selected = st.selectbox("Make: ", get_collection_list())

    # Create a selectbox for document options
    subject_selected = st.selectbox("Subject: ", get_doc_list(make_selected))
    
    # Display the information from "Issue" field
    st.write(f"Issue: {show_information_resolution(make_selected, subject_selected, field="Issue")}")
    
    # Display the information from "Information" field
    st.write(f"Information: {show_information_resolution(make_selected, subject_selected, field="Information")}")
    
    # Display the information from "Technician" field
    st.write(f"Technician: {show_information_resolution(make_selected, subject_selected, field="Technician")}")

    # Display the information from "Date" field
    st.write(f"Date: {show_information_resolution(make_selected, subject_selected, field="Date")}")


with tab3:

    # Call the function to get the collection list
    collection_list = get_collection_list()
    # Create a selectbox for 'Make' options
    make_name_selected = st.selectbox("Make:", collection_list)

    # Call the function to get the document list
    document_list = get_doc_list(make_name_selected)
    # Create a selectbox for document options
    subject_name_selected = st.selectbox("Suject:", document_list)

    # Call the function to get the field list
    fields_list_obtained = st.selectbox("Select the field to be updated:", get_field_list(make_name_selected, subject_name_selected))
    
    # Call the function to show the information from each field stored in Firestore
    information_to_be_updated = st.write(show_information_resolution(make_name_selected, subject_name_selected, fields_list_obtained))
    
    # Create a text area for the information to be updated
    information_to_be_updated = st.text_area("Enter the new information")

    # Function to update the information in Firestore
    def update_info(make_name_selected, subject_name_selected, fields_list_obtained):
        # Reference to the document in Firestore
        doc_ref = db.collection(make_name_selected).document(subject_name_selected)
        # Update the information in the based on the field selected
        doc_ref.update({"Date": datetime.datetime.now(), fields_list_obtained: information_to_be_updated})

    # Button to update the information input
    if st.button("Updated Information"):
        # Call the function to update the information in Firestore
        update_info(make_name_selected, subject_name_selected, fields_list_obtained)
        # Display a success message
        st.success("Information updated successfully!")
        # Display the updated information
        st.write(show_information_resolution(make_name_selected, subject_name_selected, fields_list_obtained))




# python -m streamlit run 'C:\Language_Projects\Language_Projects\Python\ecu_info\src\ecu_info.py'