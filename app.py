import streamlit as st
import imaplib
import email
from email.header import decode_header
import pandas as pd
from langchain import LLMChain, OpenAI
from langchain.prompts import PromptTemplate

# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

# Function to search for a key value pair 
def search(key, value, con): 
    result, data = con.search(None, key, '"{}"'.format(value))
    return data

# Function to get the list of emails under this label
def get_emails(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs

# Streamlit UI
st.title("AppTrackPro")
st.write("Sign in to your email to track your internship and job applications.")

email_provider = st.selectbox("Choose your email provider", ["Gmail", "Outlook"])
email_user = st.text_input("Email")
email_password = st.text_input("Password", type="password")

if st.button("Sign In"):
    try:
        if email_provider == "Gmail":
            imap_url = 'imap.gmail.com'
        elif email_provider == "Outlook":
            imap_url = 'outlook.office365.com'

        con = imaplib.IMAP4_SSL(imap_url)
        con.login(email_user, email_password)
        st.success("Logged in successfully!")
        
        # Searching for application emails
        con.select('Inbox')
        keywords = ["application received", "application confirmation", "application update", "interview request", "rejection", "offer"]
        emails = []
        for keyword in keywords:
            emails.extend(get_emails(search('BODY', keyword, con)))

        # Parsing emails
        email_data = []
        for msg in emails:
            for sent in msg:
                if type(sent) is tuple:
                    msg = email.message_from_bytes(sent[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    from_ = msg.get("From")
                    body = get_body(msg).decode()
                    email_data.append({"Subject": subject, "From": from_, "Body": body})

        # Categorizing emails using LLM
        llm = OpenAI(model="text-davinci-003")
        template = "Categorize the following email subjects and bodies into 'confirmation', 'interview request', 'rejection', or 'offer'.\n\nEmail: {email}\n\nCategory:"
        prompt = PromptTemplate(template=template, input_variables=["email"])
        chain = LLMChain(llm=llm, prompt=prompt)

        categorized_data = []
        for email in email_data:
            result = chain.run(email=email["Subject"] + "\n" + email["Body"])
            categorized_data.append({
                "Subject": email["Subject"],
                "From": email["From"],
                "Body": email["Body"],
                "Category": result.strip()
            })

        df = pd.DataFrame(categorized_data)
        print(df)
        st.write("Tracked Applications", df)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")



# # Importing libraries
# import imaplib, email

# user = 'yashg4509@gmail.com'
# password = 'hyun qfkw uugi ubpd'
# imap_url = 'imap.gmail.com'

# # Function to get email content part i.e its body part
# def get_body(msg):
# 	if msg.is_multipart():
# 		return get_body(msg.get_payload(0))
# 	else:
# 		return msg.get_payload(None, True)

# # Function to search for a key value pair 
# def search(key, value, con): 
# 	result, data = con.search(None, key, '"{}"'.format(value))
# 	return data

# # Function to get the list of emails under this label
# def get_emails(result_bytes):
# 	msgs = [] # all the email data are pushed inside an array
# 	for num in result_bytes[0].split():
# 		typ, data = con.fetch(num, '(RFC822)')
# 		msgs.append(data)

# 	return msgs

# # this is done to make SSL connection with GMAIL
# con = imaplib.IMAP4_SSL(imap_url) 

# # logging the user in
# con.login(user, password) 

# # calling function to check for email under this label
# con.select('Inbox') 

# # fetching emails from this user "tu**h*****1@gmail.com"
# msgs = get_emails(search('FROM', 'noreply@google.com', con))

# # Uncomment this to see what actually comes as data 
# # print(msgs) 


# # Finding the required content from our msgs
# # User can make custom changes in this part to
# # fetch the required content he / she needs

# # printing them by the order they are displayed in your gmail 
# for msg in msgs[::-1]: 
# 	for sent in msg:
# 		if type(sent) is tuple: 

# 			# encoding set as utf-8
# 			content = str(sent[1], 'utf-8') 
# 			data = str(content)

# 			# Handling errors related to unicodenecode
# 			try: 
# 				indexstart = data.find("ltr")
# 				data2 = data[indexstart + 5: len(data)]
# 				indexend = data2.find("</div>")

# 				# printing the required content which we need
# 				# to extract from our email i.e our body
# 				print(data2[0: indexend])

# 			except UnicodeEncodeError as e:
# 				pass


# import os
# import pickle
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# def authenticate_gmail():
#     creds = None
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = Credentials.from_authorized_user_info(pickle.load(token), SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds.to_json(), token)
#     return creds

# def list_messages(service):
#     results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
#     messages = results.get('messages', [])
#     if not messages:
#         print('No messages found.')
#     else:
#         print('Messages:')
#         for message in messages:
#             msg = service.users().messages().get(userId='me', id=message['id']).execute()
#             print(f"Message snippet: {msg['snippet']}")

# def main():
#     creds = authenticate_gmail()
#     service = build('gmail', 'v1', credentials=creds)
#     list_messages(service)

# if __name__ == '__main__':
#     main()
