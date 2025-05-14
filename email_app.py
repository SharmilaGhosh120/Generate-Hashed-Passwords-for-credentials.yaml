import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load environment variables from .env file
load_dotenv()

# Email configuration from environment variables
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL"),
    "sender_password": os.getenv("SENDER_PASSWORD")
}

def generate_hashed_passwords():
    """
    Function to generate hashed passwords for credentials.yaml
    """
    passwords = ['admin123', 'user123']  # Passwords for admin and user1
    hasher = stauth.Hasher()
    hashed_passwords = hasher.hash(passwords)
    return hashed_passwords

# Check if credentials.yaml exists, otherwise prompt to generate hashed passwords
try:
    with open('credentials.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.warning("credentials.yaml not found. Generate hashed passwords below and create the file.")
    config = None

# Initialize authenticator if config is available
if config:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    # Render login form
    login_result = authenticator.login(location='main')
    if login_result is not None:
        name, authentication_status, username = login_result
    else:
        name, authentication_status, username = None, None, None
else:
    authentication_status = None
    name = None

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Welcome *{name}*')

    # Streamlit UI for sending emails
    st.title("Ky'ra Email Sending App")

    with st.form("email_form"):
        to_email = st.text_input("Recipient Email", placeholder="recipient@example.com")
        subject = st.text_input("Subject", placeholder="Enter email subject")
        html_content = st.text_area("HTML Content", placeholder="Enter HTML content for the email")
        submitted = st.form_submit_button("Send Email")

        if submitted:
            if not to_email or not subject or not html_content:
                st.error("All fields are required.")
            else:
                try:
                    send_email(to_email, subject, html_content)
                    st.success(f"✅ Email sent successfully to {to_email}")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {str(e)}")
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None and not config:
    st.warning('Please generate hashed passwords and create credentials.yaml')
elif authentication_status == None:
    st.warning('Please enter your username and password')

def send_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Function to send email using SMTP
    """
    try:
        # Validate email configuration
        if not all([EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"]]):
            raise Exception("Sender email or password not configured in .env file")

        # Create MIME message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()  # Enable TLS
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)

    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")

# Section to generate hashed passwords
st.subheader("Generate Hashed Passwords for credentials.yaml")
if st.button("Generate Hashed Passwords"):
    hashed_passwords = generate_hashed_passwords()
    st.write("Copy the following hashed passwords into your credentials.yaml file:")
    st.code(f"""
admin: {hashed_passwords[0]}
user1: {hashed_passwords[1]}
""")
    st.markdown("""
    **Example credentials.yaml:**
    ```yaml
    cookie:
      expiry_days: 30
      key: superstrongkey
      name: email_app_cookie
    credentials:
      usernames:
        admin:
          email: admin@example.com
          name: Admin User
          password: {hashed_passwords[0]}
        user1:
          email: user1@example.com
          name: User One
          password: {hashed_passwords[1]}
    ```
    Save this in a file named `credentials.yaml` in the same directory as `email_app.py`.
    """)

# Instructions for running the app
st.markdown("""
### How to Run the App
1. Save this code in a file named `email_app.py`.
2. Create a `.env` file in the same directory with the following content:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_specific_password
```
   Replace `your_email@gmail.com` with your email and `your_app_specific_password` with an app-specific password (e.g., for Gmail, generate one in your Google Account settings).
3. Create a `credentials.yaml` file with user credentials (use the hashed passwords generated above).
4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Streamlit app:
   ```bash
   streamlit run email_app.py
   ```
6. Open the provided URL (usually `http://localhost:8501`) in your browser.
""")