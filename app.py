import streamlit as st
import imaplib
import email
from email.header import decode_header
import pandas as pd
import streamlit_authenticator as stauth

# Email Scraping Functions
def fetch_emails(email_user, email_password, email_service):
    if email_service == "Gmail":
        imap_url = 'imap.gmail.com'
    elif email_service == "Outlook":
        imap_url = 'imap-mail.outlook.com'
    else:
        st.error("Unsupported email service")
        return pd.DataFrame()

    # Connect to the email server
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(email_user, email_password)
    mail.select("inbox")

    # Search for emails
    status, messages = mail.search(None, 'ALL')

    email_list = []
    if status == "OK":
        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            from_ = msg.get("From")
            email_body = msg.get_payload(decode=True).decode()
            
            # Check for application status keywords
            status = "Pending"
            if any(keyword in subject.lower() for keyword in ["interview", "schedule", "invitation"]):
                status = "Interview Request"
            elif any(keyword in subject.lower() for keyword in ["rejected", "declined", "unsuccessful"]):
                status = "Rejected"
            elif any(keyword in subject.lower() for keyword in ["offer", "congratulations", "accepted"]):
                status = "Offer"

            email_list.append([subject, from_, status])

    mail.logout()
    return pd.DataFrame(email_list, columns=["Subject", "From", "Status"])

# Streamlit Authentication
credentials = {
    "usernames": {
        "your_username": {
            "name": "Your Name",
            "password": "your_password",
        }
    }
}
authenticator = stauth.Authenticate(credentials, "app_home", "abcdef", cookie_expiry_days=30)

# Streamlit App
def main():
    st.title("Email Application Tracker")

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        st.sidebar.success(f"Welcome {name}!")
        st.sidebar.write("Enter your email credentials to fetch application emails.")

        email_service = st.sidebar.selectbox("Email Service", ["Gmail", "Outlook"])
        email_user = st.sidebar.text_input("Email Address")
        email_password = st.sidebar.text_input("Email Password", type="password")

        if st.sidebar.button("Fetch Emails"):
            with st.spinner("Fetching emails..."):
                emails_df = fetch_emails(email_user, email_password, email_service)
                st.dataframe(emails_df)

                if not emails_df.empty:
                    st.write("Tracking applications...")
                    st.dataframe(emails_df)

                    st.write("Manually track additional details:")
                    st.write("Please enter additional information for each application as needed.")
                    
                    for index, row in emails_df.iterrows():
                        st.write(f"Application from {row['From']}:")
                        login_credentials = st.text_input(f"Login credentials for {row['From']}", key=f"login_{index}")
                        additional_notes = st.text_area(f"Additional notes for {row['From']}", key=f"notes_{index}")

                        # Save additional details
                        emails_df.at[index, "Login Credentials"] = login_credentials
                        emails_df.at[index, "Additional Notes"] = additional_notes

                    st.write("Updated Applications Table:")
                    st.dataframe(emails_df)

    elif authentication_status == False:
        st.error("Username/password is incorrect")
    elif authentication_status == None:
        st.warning("Please enter your username and password")

if __name__ == "__main__":
    main()
