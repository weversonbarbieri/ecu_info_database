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
    doc_ref = db.collection(make_name).document(subject)
    # Stores the input's timestamp
    time_info = datetime.datetime.now()
    # Set the data in the document
    doc_ref.set(
        {
            'Technician': technician,
            'Date': time_info,
            'Issue': issue,
            'Information': information
            }
            )


# Create two tabs in the Streamlit app
tab1, tab2 = st.tabs(["Enter Information", "Information Updated"])

with tab1:

    # Options for the 'Technician' dropdown menu
    technicians_list = ["Adeosun", "Martin", "Tavassika", "Weverson"]
    # Create a selectbox for 'Technician' options
    technician = st.selectbox("Technician:", technicians_list)

    # Options for the 'Make' dropdown menu
    make_options = ['All Makes', 'Chevrolet', 'Chrysler', 'Ford', 'GM', 'GMC', 'Jeep', 'Lexus', 'Mazda', 'Nissan', 'Toyota']
    # Create a selectbox for 'Make' options
    make_name = st.selectbox('Make', make_options)
    # Create a selectbox for 'Subject' options
    subject = st.text_input('Enter the Subject (ENTER THE INFO IN CAPS LETTERS)')

    # Create a text input for 'Issue'
    issue = st.text_input("Enter the Issue", key='issue_input')

    # Create a text area for 'Information'
    information = st.text_area('Enter the information')

    # Button to save the text
    if st.button('Save Text'):
        # Call the function to add text to Firestore
        add_text(issue, information)
        # Display a success message
        st.success(f'Information added successfully!')

with tab2:
    # Get all collections from the Firestore database
    collections = db.collections()
    collection_list = []
    # Append the collection IDs to the list
    for collection in collections:
        collection_list.append(collection.id)
        # Create a selectbox for 'Make' options
    make_selected = st.selectbox("Make: ", collection_list)
    # Reference to the selected collection
    subjects_ref = db.collection(make_selected)
    # Get all documents in the selected collection
    subjects = subjects_ref.get()

    subject_list = []
    # Append the document IDs to the list
    for sub in subjects:
        subject_list.append(sub.id)
        # Create a selectbox for 'Subject' options
    subject_selected = st.selectbox("Subject: ", subject_list)
    # Reference to the selected document in the selected collection
    information = db.collection(make_selected).document(subject_selected)
    # Get the document data
    info_ref = information.get()
    # Convert the document data to a dictionary
    info_dict = info_ref.to_dict()
    # Get the 'Issue' field from the dictionary
    issue = info_dict.get('Issue', '')
    # Get the 'Information' field from the dictionary
    information_added = info_dict.get('Information', '')
    # Get the 'Date' field from the dictionary
    timestamp_info = info_dict.get('Date', '')

    # Display the input's date
    st.write(f"Input's date: {timestamp_info}")
    # Display the technician who input the info
    st.write(f"Technician: {technician}")
    # Display the 'Issue' field
    st.write(f"Issue: {issue}")

    # Display the 'Information' field
    st.write(f"Information: {information_added}")


# python -m streamlit run 'C:\Language_Projects\Language_Projects\Python\ecu_info\src\ecu_info.py'
