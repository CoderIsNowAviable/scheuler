from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

# Load Jinja2 Environment
env = Environment(loader=FileSystemLoader("templates"))

def generate_verification_code():
    verification_code = str(random.randint(10000, 99999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    return verification_code, expires_at

def send_email(user_email: str, subject: str, html_content: str):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    # Create email
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {user_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_verification_email(user_email: str, verification_code: str):
    template = env.get_template("verification_email.html")
    html_content = template.render(user_email=user_email, verification_code=verification_code)
    send_email(user_email, "Your Verification Code", html_content)

def send_password_reset_email(user_email: str, reset_link: str):
    template = env.get_template("password_reset_email.html")
    html_content = template.render(user_email=user_email, reset_link=reset_link)
    send_email(user_email, "Password Reset Request", html_content)
