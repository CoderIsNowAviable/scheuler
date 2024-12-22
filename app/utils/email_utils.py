import os
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()

def generate_verification_code():
    return str(random.randint(10000, 99999))  # Generate a 6-digit code

def send_verification_email(user_email: str, verification_code: str):
    # Gmail SMTP configuration
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = user_email
    
    # Email content
    subject = "Your Verification Code"
    body = f"Your verification code is {verification_code}.\nIt will expire in 5 minutes."

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Verification code sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
