import os
from dotenv import load_dotenv, dotenv_values
import pyrebase
import streamlit as st
import firebase_admin
import json
from firebase_admin import credentials, firestore, auth
from firebase_admin import db

# Load environment variables
load_dotenv()

# Configuration key
firebaseConfig = {
  'apiKey': os.getenv('FIREBASE_API_KEY'),
  'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
  'projectId': os.getenv('FIREBASE_PROJECT_ID'),
  'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
  'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
  'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
  'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
  'appId': os.getenv('FIREBASE_APP_ID'),
  'appId': os.getenv('FIREBASE_APP_ID'),
  'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID')
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
# Get auth service
auth = firebase.auth() 

# Get database service
db = firebase.database() 
# Get storage service
storage = firebase.storage() 

# Set app title
st.title("ECU Database App")

# Authentication
choise = st.sidebar.selectbox("Login/SignUp", ["Login", "Sign up"])

# Email and password input
email = st.sidebar.text_input("Please enter your email address")
password = st.sidebar.text_input("Please enter your passowrd", type='password')

# Handle input
if choise == 'Sign up':

  handle = st.sidebar.text_input("Please input your app handle name", value='Default')
  # Submit button
  submit = st.sidebar.button("Create my account")
  if submit:
    # Create user
    user = auth.create_user_with_email_and_password(email, password)
    # Show success message
    st.success("Your account is created sucessfully")
    # Sign in user
    user = auth.sign_in_with_email_and_password(email, password)
    # Store handle
    db.child(user['localId']).child('Handle').set(handle)
    # Store user ID
    db.child(user['localId']).child('ID').set(user['localId'])
    # Welcome message
    st.title('Welcome' + handle)
    # Login info
    st.info('Login via login drop down selection')

# Function to add make, subject issue and information
def add_make_subject_issue_info(make, subject, issue, info, tech):
  doc_ref = db.collection(make).document(subject)
  doc_ref.set({issue: {"Information": info, "Technician": tech}})
  return True

# Function to add subject
def add_subject(make, subject_input, issue, tech):
  doc_ref = db.collection(make).document(subject_input)
  doc_ref.set({issue: {"Technician": tech}})
  return True

# Function to update issue and information
def add_issue_information(make, subject, issue, info_input, tech):
  doc_ref = db.collection(make).document(subject)
  doc_ref.update({issue: {"Information": info_input, "Technician": tech}})
  return True

# Function to update existing issue
def update_existint_issue(make, subject, issue, information_input, tech):
  doc_ref = db.collection(make).document(subject)
  doc_ref.update({issue: {"Information": information_input, "Technician": tech}})
  return True

# Function to get the collection list
def get_collection_list():
  collections = db.collections()
  collection_list = []
  for collection in collections:
    collection_list.append(collection.id)
  return collection_list

# Function to get the document list
def get_document_list(make_name):
  subjects_ref = db.collection(make_name)
  subjects = subjects_ref.get()
  subject_list = []
  for sub in subjects:
    subject_list.append(sub.id)
  return subject_list

# Function to get the issue list
def get_issue_list(make_given, subject_given):
  doc_ref = db.collection(make_given).document(subject_given)   
  info_ref = doc_ref.get().to_dict()
  issue_list = []
  for issue in info_ref: 
    issue_list.append(issue)
  return issue_list

# Function to show the information
def show_information(make_given, subject_given):
  doc_ref = db.collection(make_given).document(subject_given)
  info_ref = doc_ref.get().to_dict()
  return info_ref

# Function to delete a subject
def subject_to_delete(make, subject):
  subject_ref = db.collection(make).document(subject).delete()
  return True

# Function to delete an issue
def issue_to_delete(make, subject, issue):
  issue_ref = db.collection(make).document(subject).update({issue: firestore.DELETE_FIELD})
  return True


# Handle login
if choise == "Login":
    if st.sidebar.checkbox("Login"):
        # Try to login
        try:
            # Sign in user using google cloud attentication
            user = auth.sign_in_with_email_and_password(email, password)
            # After loggin in show the user the options available
            options = st.radio('Go to', ['ECU Database', 'Input Section', "Delete"], horizontal=True)
            # Section to input data starting for the make, subject, issue and information
            if options == 'Input Section':
                # Set 4 tabs  
                tab1, tab2, tab3, tab4 = st.tabs(["Add Make", "Add Subject", "Add Issue", "Update Information"])

                # Tab to add make, subject, issue and information
                with tab1:
                  # Load the key from the secrets
                  key_dict = json.loads(st.secrets["textkey"])
                  # Initialize Firebase
                  if not firebase_admin._apps: 
                    cred = credentials.Certificate(key_dict)
                    firebase_admin.initialize_app(cred)
                  # Initialize Firestore
                  db = firestore.client()
                  
                  # Try to add the make, subject, issue and information
                  try:
                    # Input text to enter the make
                    make = st.text_input("Enter Make:", key="make")
                    # Options to select the technician
                    technician = st.radio("Technician: ", ["Martin", "Weverson"], horizontal=True, key="technician")
                    # Enter the subject
                    subject = st.text_input("Enter Subject:", key="subject")
                    # Enter the issue
                    issue = st.text_input("Enter issue:", key="issue")
                    # Enter the information
                    text_input = st.text_area("Enter the Information:", key="text_input")
                    # Condition when the user clicks the button
                    if st.button("Update Information"):
                      # Call the fuction to add make, subject, issue and information
                      add_make_subject_issue_info(make, subject, issue, text_input, technician)
                      # Display a success message
                      st.success(f"Make, Subject and Issue added successfully!")
                  
                  # Excepction when an error occurs
                  except Exception as e:
                     st.write(f"Error: {e}")

                # Tab to add a new subject and issue
                with tab2:
                  
                  # Initialize Firebase
                  if not firebase_admin._apps: 
                    # Load the key from the secrets
                    key_dict = json.loads(st.secrets["textkey"])
                    # Initialize Firebase
                    cred = credentials.Certificate(key_dict)
                    firebase_admin.initialize_app(cred)
                  # Initialize Firestore
                  db = firestore.client()
                  
                  # To add a new subject and issue
                  try:
                    # Get a list of makes to select the make needed
                    make_list = st.selectbox("Select the Make:", get_collection_list())
                    # Select the technician
                    technician_selected = st.radio("Technician: ", ["Martin", "Weverson"], horizontal=True, key="technician_selected")
                    # Input the subject
                    subject_given = st.text_input("Enter Subject:", key="subject_given")
                    # Input the issue
                    issue_given = st.text_input("Enter the new Issue (please, insert _ INSTEAD OF spaces):", key="issue_given")
                    
                    # Condition when the user clicks the button
                    if st.button("Add Subject"):
                      # Call the fuction to add a new subject
                      add_subject(make_list, subject_given, issue_given, technician_selected)
                      # Sucess message when the subjet was successfully added 
                      st.success(f"Subject added successfully!")
                  
                  # Excepction when an error occurs
                  except Exception as e:
                     st.write(f"Error: {e}")
               
                with tab3:
                  # Load the key from the secrets
                  key_dict = json.loads(st.secrets["textkey"])
                  # Initialize Firebase
                  if not firebase_admin._apps: 
                    cred = credentials.Certificate(key_dict)
                    firebase_admin.initialize_app(cred)
                  # Initialize Firestore
                  db = firestore.client()

                  try:
                    # Select the make from the list of makes
                    make_new_issue = st.selectbox("Select the Make:", get_collection_list(), key="make_new_issue")
                    # Select the technician from the list of technician
                    technician_new_issue = st.radio("Select the Technician:", ["Martin", "Weverson"], horizontal=True, key="technician_new_issue")
                    # Get the list of existing subjects for the selected make
                    existing_subjects_list = get_document_list(make_new_issue)
                    # Select the subject from the list of existing subjects
                    existing_subjects_selected = st.selectbox("Select the Subject:", existing_subjects_list, key="existing_subjects_selected")
                    # Input the new issue
                    new_issue = st.text_input("Enter the new Issue (please, insert _ INSTEAD OF spaces):", key="new_issue")
                    # Input the information for the new issue
                    information_new_issue = st.text_area("Enter the information:", key="information_new_issue")
                    
                    # Condition when the user clicks the button to add the issue
                    if st.button("Add Issue"):
                      # Call the function to add the issue information
                      add_issue_information(make_new_issue, existing_subjects_selected, new_issue, information_new_issue, technician_new_issue)
                      # Display a success message
                      st.success(f"Issue added successfully!")

                  # Exception handling when an error occurs
                  except Exception as e:
                     st.write(f"Failed: {e}")

                with tab4:
                  # Load the key from the secrets
                  key_dict = json.loads(st.secrets["textkey"])
                  # Initialize Firebase if not already initialized
                  if not firebase_admin._apps: 
                    cred = credentials.Certificate(key_dict)
                    firebase_admin.initialize_app(cred)
                  # Initialize Firestore
                  db = firestore.client()
                  
                  try:
                    # Select the make from the list of makes
                    make_input = st.selectbox("Select the Make:", get_collection_list(), key="make_input")
                    # Select the technician from the list of technicians
                    technician_input = st.radio("Select the Technician:", ["Martin", "Weverson"], horizontal=True, key="technician_input")
                    # Get the list of documents (subjects) for the selected make
                    update_info_documento_list = get_document_list(make_input)
                    # Select the subject from the list of documents
                    subject_input = st.selectbox("Select the Subject:", update_info_documento_list, key="subject_input")
                    # Get the list of issues for the selected make and subject
                    issue_options = get_issue_list(make_input, subject_input)
                    # Select the issue from the list of issues
                    issue_input = st.selectbox("Select the issue:", issue_options, key="issue_input")
                    # Input the information to update the issue
                    update_info = st.text_area("Enter the information:", key="update_info")
                    
                    # Condition when the user clicks the button to update the information
                    if st.button("Update Information", key="Update Information"):
                      # Call the function to update the existing issue with the new information
                      update_existint_issue(make_input, subject_input, issue_input, update_info, technician)
                      # Display a success message
                      st.success(f"Information added successfully!")
                  
                  # Exception handling when an error occurs
                  except Exception as e:
                     st.write(f"Failed: {e}")

            elif options == "ECU Database":
                # Load the key from the secrets
                key_dict = json.loads(st.secrets["textkey"])
                # Initialize Firebase if not already initialized
                if not firebase_admin._apps: 
                  cred = credentials.Certificate(key_dict)
                  firebase_admin.initialize_app(cred)
                # Initialize Firestore
                db = firestore.client()

                try:
                  # Select the make from the list of makes
                  make_chosen = st.selectbox("Select the Make:", get_collection_list())
                  # Get the list of documents (subjects) for the selected make
                  update_info_documento_list = get_document_list(make_chosen)
                  # Select the subject from the list of documents
                  subject_chosen = st.selectbox("Select the Subject:", update_info_documento_list)
                  # Get the list of issues for the selected make and subject
                  issue_chosen_list = get_issue_list(make_chosen, subject_chosen)
                  # Select the issue from the list of issues
                  issue_chosen = st.selectbox("Select the issue:", issue_chosen_list)
                  # Get the information for the selected make, subject, and issue
                  chosen_items_list = show_information(make_chosen, subject_chosen)
                  # Filter the dictionary to get the information for the selected issue
                  dict_filtered = chosen_items_list[issue_chosen]
                  
                  # Display the information for each topic and value in the filtered dictionary
                  for topic, value in dict_filtered.items():
                    st.write(f"{topic}: {value}")

                 # Exception handling when an error occurs
                except Exception as e:
                     st.write(f"Failed: {e}")

            elif options == "Delete":
              # Select the option to be deleted: Subject or Issue
              option_to_delete = st.selectbox("Select the option to be deleted:", ["Subject", "Issue"])
              
              if option_to_delete == "Subject":
                  # Load the key from the secrets
                  key_dict = json.loads(st.secrets["textkey"])
                  # Initialize Firebase if not already initialized
                  if not firebase_admin._apps: 
                      cred = credentials.Certificate(key_dict)
                      firebase_admin.initialize_app(cred)
                  # Initialize Firestore
                  db = firestore.client()
              
                  try:
                      # Select the make from the list of makes
                      makes_available = st.selectbox("Select the Make:", get_collection_list(), key="makes_available")
                      # Get the list of subjects for the selected make
                      subjects_available_list = get_document_list(makes_available)
                      # Select the subject to be deleted from the list of subjects
                      subject_to_be_deleted = st.selectbox("Select the Subject to be Deleted:", subjects_available_list, key="subject_to_be_deleted")

                      # Condition when the user clicks the button to delete the subject
                      if st.button(f"Delete { subject_to_be_deleted}"):
                          try:
                              # Call the function to delete the selected subject
                              subject_to_delete(makes_available, subject_to_be_deleted)
                              # Display a success message
                              st.success("Subject deleted sucessfully!")
                          except Exception as e:
                              st.write(f"Error: {e}")

                  # Exception handling when an error occurs
                  except Exception as e:
                      st.write(f"Error: {e}")
              
              # Condition when selecting "Issue" option
              elif option_to_delete == "Issue":
                  # Load the key from the secrets
                  key_dict = json.loads(st.secrets["textkey"])                  
                  # Initialize Firebase if not already initialized
                  if not firebase_admin._apps: 
                      cred = credentials.Certificate(key_dict)
                      firebase_admin.initialize_app(cred)
                  # Initialize Firestore
                  db = firestore.client()
                  try:
                      # Select the make from the list of makes
                      makes_options = st.selectbox("Select the Make:", get_collection_list(), key="makes_options")
                      # Get the list of subjects for the selected make
                      subjects_options_list = get_document_list(makes_options)
                      # Select the subject from the list of subjects
                      subject_options = st.selectbox("Select the Subject:", subjects_options_list, key="subject_options")
                      # Get the list of issues for the selected make and subject
                      issue_options_list = get_issue_list(makes_options, subject_options)
                      # Select the issue to be deleted from the list of issues
                      issue_to_be_deleted = st.selectbox("Select the issue to be Deleted:", issue_options_list, key="issue_to_be_deleted")

                      # Condition when the user clicks the button to delete the issue
                      if st.button(f"Delete {issue_to_be_deleted}"):
                          # Call the function to delete the selected issue
                          issue_to_delete(makes_options, subject_options, issue_to_be_deleted)
                          # Display a success message
                          st.success("Issue deleted successfully!")

                  # Exception handling when an error occurs
                  except Exception as e:
                      st.write(f"Error: {e}")

        # This is the exception handling when the user and password are incorrect                
        except:
            st.write("Enter the correct login and password")
  


# python -m streamlit run "C:\Language_Projects\Language_Projects\Python\ecu_info\src\ecu_info.py"