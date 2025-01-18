import streamlit as st
import requests
import re
import base64
import os
from functools import partial
import json
import uuid
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

# URL of the Rasa API (assuming it's running locally on port 5005)
RASA_URL = "http://localhost:2005/webhooks/rest/webhook"
download_foler = "/home/amitshendgepro/rasa_bot/outputs"
# download_foler = "/Users/amitshendge/Documents/rasa_bot/outputs"

bas_path = download_foler.replace('outputs', '')

load_dotenv()

# Azure AD credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read"]  # Microsoft Graph API scope
ALLOWED_GROUP_ID = os.getenv("ADMIN_GROUP_ID")

# MSAL instance
app_instance = ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

def generate_download_link(file_path, link_text="Download File"):
    """
    Generates a hyperlink to download any file.
    
    Parameters:
    - file_path: Path to the file.
    - link_text: Text to display for the download link.
    
    Returns:
    - str: HTML link for downloading the file.
    """
    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()
            file_name = file_path.split("/")[-1]  # Extract file name from path
            mime_type = "application/octet-stream"  # Generic MIME type for files
            b64_file = base64.b64encode(file_bytes).decode()  # Encode file to Base64
            href = f'<a href="data:{mime_type};base64,{b64_file}" download="{file_name}">{link_text}</a>'
            return href
    except Exception as e:
        return f"Error generating download link: {e}"

# Function to send user message to Rasa and get the response
def get_rasa_response(user_message):
    print("user_message", user_message)
    payload = {"sender":st.session_state.session_id,"message": user_message}
    response = requests.post(RASA_URL, json=payload)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        return [{"text": "Sorry, I couldn't get a response from the bot."}]

def clean_text(default_message=None, store_message=True):
    user_message = st.session_state['user_message']
    if default_message:
        user_message = default_message
    print("user_message", user_message)
    if user_message:
        # Append user's message to the session state
        if store_message:
            st.session_state.messages.append({"role": "user", "text": user_message})
        # Get response from Rasa
        bot_response = get_rasa_response(user_message)
    print("bot_response", bot_response)
    # Append bot's response to the session state
    for message in bot_response:
        if 'image' in message:
            st.session_state.messages.append({"role": "bot", "image": message.get('image')})
        elif 'custom' in message:
            payload = message.get('custom')
            if payload.get('type') == 'download_file':
                download_link = generate_download_link(os.path.join(download_foler, payload.get('file_name')), link_text="Download File")
                st.session_state.messages.append({"role": "bot", "download": download_link})
            elif payload.get('type') == 'select_options':
                st.session_state.messages.append({"role": "bot", "text": "Please select one of the following options:"})
                for option in payload.get('payload'):
                    st.session_state.messages.append({"role": "bot", "button": option.get('title')})
                    st.session_state.buttons_message.append({"role": "bot", "button": option.get('title')})
        else:
            st.session_state.messages.append({"role": "bot", "text": message.get('text')})
    if not default_message:
        st.session_state['user_message']=""

def button_callback(m):
    # st.session_state['user_message'] = message['button']
    for i in st.session_state.buttons_message[:]:
        st.session_state.messages.remove(i)
        st.session_state.buttons_message.remove(i)
    clean_text(m)

def login():
    """Generate Azure AD login URL"""
    state = str(uuid.uuid4())  # Random session state
    auth_url = app_instance.get_authorization_request_url(
        SCOPE, state=state, redirect_uri=REDIRECT_URI
    )
    return auth_url

def get_user_info(code):
    try:
        result = app_instance.acquire_token_by_authorization_code(
            code, scopes=SCOPE, redirect_uri=REDIRECT_URI
        )
        print("result", result)
        if "error" in result:
            return None
        claims = result.get("id_token_claims", {})
        return {
            "name": claims.get("name"),
            "groups": claims.get("groups", [])
        }
    except Exception as e:
        st.error(f"Error during authentication: {str(e)}")
        return None
    
# Initialize session state to store conversation history if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'buttons_message' not in st.session_state:
    st.session_state.buttons_message = []
if 'button_clicked' not in st.session_state:
    st.session_state['button_clicked'] = False
if 'files' not in st.session_state:
    st.session_state.files = [i[:-5] for i in list(os.listdir(bas_path + "app/actions/form_feilds_mapping_v2"))]
if 'forms' not in st.session_state:
    st.session_state.forms = json.load(open(bas_path + "app/actions/form_filling_code/forms_subset.json"))
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Step 1: Select category

if st.session_state['user'] is None:
    print(st.session_state['user'])
    st.title("Please log in to continue")
    login_url = login()
    st.markdown(f'<a href="{login_url}" target="_self">Login with Azure AD</a>', unsafe_allow_html=True)
    
else:
    st.title("Form Filling Chatbot")
    category = st.selectbox("Select Form Category", list(st.session_state.forms.keys()))

    if category:
        selected_form = st.selectbox(
            f"Select a form from {category}",
            ["Select Form here"] + st.session_state.forms[category]
        )
    # st.session_state['button_clicked'] = False
    # option = st.selectbox("Choose an option:", ["Select Form here"] + st.session_state.get('files'), key="option")
    def button_action():
        if selected_form != "Select Form here":
            print("option", f'/trigger_action{{"param": "{selected_form}"}}')
            response = clean_text(default_message=f'/trigger_action{{"param": "{selected_form}"}}', store_message=False)
    st.button("Submit", on_click=button_action)
    # if option != "None":
    #     response = clean_text(option)

    # st.write("Available forms now:\n1. Addendum Lease - K1384,\n2. Addendum Sale - K1117, \n3. Extension of Review Period for Resale Certificate - K1389, \n4. K1388 - Payment Plan Addendum \n5. Disclosure of Brokerage Relationship - K1207")
    # User input text box
    user_message = st.text_input("Say Hi to the bot:", key="user_message", on_change=clean_text)


    # Display the conversation history
    for message in st.session_state.messages[::-1]:
        if message['role'] == 'user':
            st.write(f"You: {message['text']}")
        else:
            if 'image' in message:
                st.image(message['image'], width=200)
            elif 'download' in message:
                st.write(message['download'], unsafe_allow_html=True)
            elif 'button' in message:
                st.button(message['button'], key=message['button'], on_click=partial(button_callback, message['button']))
            else:
                st.write(f"Bot: {message['text']}")
query_params = st.query_params
print("query_params", query_params)
if 'code' in query_params:
    code = query_params['code']
    user_info = get_user_info(code)
    print("user_info", user_info)
    if user_info:
        if ALLOWED_GROUP_ID not in user_info['groups']:
            st.session_state['user'] = None
            st.warning("Access Denied: You are not authorized.")
        else:
            print("Done")
            st.session_state['user'] = user_info
            st.query_params.clear()
            st.rerun()
    else:
        st.warning("Authentication failed!")
