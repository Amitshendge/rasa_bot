import streamlit as st
import requests
import re
import base64
import os

# URL of the Rasa API (assuming it's running locally on port 5005)
RASA_URL = "http://localhost:2005/webhooks/rest/webhook"
download_foler = "/home/amitshendgepro/rasa_bot/outputs"
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
    payload = {"message": user_message}
    response = requests.post(RASA_URL, json=payload)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        return [{"text": "Sorry, I couldn't get a response from the bot."}]

def clean_text():
    user_message = st.session_state['user_message']
    if user_message:
        # Append user's message to the session state
        st.session_state.messages.append({"role": "user", "text": user_message.replace("-", " ")})

        # Get response from Rasa
        bot_response = get_rasa_response(user_message)

    # Append bot's response to the session state
    for message in bot_response:
        if 'image' in message:
            st.session_state.messages.append({"role": "bot", "image": message.get('image')})
        elif 'custom' in message:
            download_link = generate_download_link(os.path.join(download_foler, message.get('custom')), link_text="Download File")
            st.session_state.messages.append({"role": "bot", "download": download_link})
        else:
            st.session_state.messages.append({"role": "bot", "text": message.get('text')})
    st.session_state['user_message']=""

    
# Initialize session state to store conversation history if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.title("Form Filling Chatbot")
st.write("Available forms now:\n1. Addendum Lease - K1384,\n2. Addendum Sale - K1117, \n3. Extension of Review Period for Resale Certificate - K1389, \n4. K1388 - Payment Plan Addendum")
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
        else:
            st.write(f"Bot: {message['text']}")
