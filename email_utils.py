# email_utils.py
import os
import yagmail
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Initialize yagmail client
yag = yagmail.SMTP(EMAIL_ADDRESS, APP_PASSWORD)

def send_email(to, subject, body):
    """
    Send an email using Gmail.

    Args:
        to (str): Recipient email address
        subject (str): Email subject
        body (str/int/float): Email content (will be converted to string)
    """
    # Ensure the body is a string
    if not isinstance(body, str):
        body = str(body)

    try:
        yag.send(to=to, subject=subject, contents=body)
        print(f"[INFO] Email sent to {to}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")