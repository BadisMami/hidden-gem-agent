import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def send_sms_alert(body):
    """
    Send an SMS alert via an email-to-SMS carrier gateway (e.g. Verizon's
    number@vtext.com, T-Mobile's number@tmomail.net) if configured.

    Returns True if a message was sent, False if SMS is not configured
    (this is optional - internship discovery works without it).
    """

    sender_address = os.environ.get("EMAIL_SENDER_ADDRESS")
    sender_app_password = os.environ.get("EMAIL_APP_PASSWORD")
    phone_number = os.environ.get("NOTIFICATION_PHONE_NUMBER")
    carrier_gateway = os.environ.get("SMS_CARRIER_GATEWAY")

    if not all(
        [sender_address, sender_app_password, phone_number, carrier_gateway]
    ):
        print("SMS alerts not configured (missing env vars). Skipping.")
        return False

    to_address = f"{phone_number}@{carrier_gateway}"

    message = EmailMessage()
    message["From"] = sender_address
    message["To"] = to_address
    message["Subject"] = ""
    message.set_content(body)

    try:

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as smtp:

            smtp.starttls()
            smtp.login(sender_address, sender_app_password)
            smtp.send_message(message)

    except Exception as e:
        print(f"Failed to send SMS alert: {e}")
        return False

    print(f"SMS alert sent to {to_address}")

    return True


if __name__ == "__main__":
    send_sms_alert("Hidden Gem Agent Test")
