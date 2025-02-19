import os
import uuid
import requests
import streamlit as st
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
from functools import partial
import base64
import json

# Load environment variables
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

# Streamlit authentication logic
def login():
    """Generate Azure AD login URL"""
    state = str(uuid.uuid4())  # Random session state
    auth_url = app_instance.get_authorization_request_url(
        SCOPE, state=state, redirect_uri=REDIRECT_URI
    )
    return auth_url

def get_user_info(code):
    """Exchange the authorization code for an access token and get user info"""
    result = app_instance.acquire_token_by_authorization_code(
        code, scopes=SCOPE, redirect_uri=REDIRECT_URI
    )

    if "error" in result:
        return None

    # Get ID token claims
    claims = result.get("id_token_claims", {})
    print(claims)
    user_info = {
        "name": claims.get("name"),
        "groups": claims.get("groups", [])
    }
    return user_info

# Initialize session state for user data
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'state' not in st.session_state:
    st.session_state['state'] = None

# Check if user is authenticated
if st.session_state['user'] is None:
    st.title("Please log in to continue")
    login_url = login()
    st.markdown(f'<a href="{login_url}" target="_self">Login with Azure AD</a>', unsafe_allow_html=True)

else:
    print("GG")
    st.title(f"Welcome {st.session_state['user']['name']}!")
    # Here, you can now show the main content of your app
    category = st.selectbox("Select Form Category", list(st.session_state.forms.keys()))

    # Add your form handling and chatbot logic here...

# Handle the redirect URL after authentication
if 'code' in st.experimental_get_query_params():
    code = st.experimental_get_query_params()['code'][0]
    user_info = get_user_info(code)
    
    if user_info:
        # Validate group membership (if necessary)
        if ALLOWED_GROUP_ID not in user_info['groups']:
            st.session_state['user'] = None
            st.warning("Access Denied: You are not authorized.")
        else:
            st.session_state['user'] = user_info
            st.experimental_rerun()
    else:
        st.session_state['user'] = None
        st.warning("Authentication failed!")
