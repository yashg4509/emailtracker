import streamlit as st
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials

# Access credentials from Streamlit secrets
client_secrets = {
    "web": {
        "client_id": st.secrets["GOOGLE_CREDENTIALS"]["client_id"],
        "project_id": st.secrets["GOOGLE_CREDENTIALS"]["project_id"],
        "auth_uri": st.secrets["GOOGLE_CREDENTIALS"]["auth_uri"],
        "token_uri": st.secrets["GOOGLE_CREDENTIALS"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["GOOGLE_CREDENTIALS"]["auth_provider_x509_cert_url"],
        "client_secret": st.secrets["GOOGLE_CREDENTIALS"]["client_secret"]
    }
}

# Save the client secrets to a temporary file
import json
import tempfile

with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".json") as temp_file:
    json.dump(client_secrets, temp_file)
    client_secrets_file = temp_file.name

# Use the credentials to build the Gmail API resource
credentials = get_gmail_credentials(
    scopes=["https://mail.google.com/"],
    client_secrets_file=client_secrets_file,
    token_file="token.json"
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)
