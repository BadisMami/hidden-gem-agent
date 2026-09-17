import os

from dotenv import load_dotenv

load_dotenv()


def send_sms_alert(body):
    """
    Send an SMS alert via Twilio if credentials are configured.

    Returns True if a message was sent, False if SMS is not configured
    (Twilio is optional - internship discovery should work without it).
    """

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    to_number = os.environ.get("NOTIFICATION_PHONE_NUMBER")

    if not all([account_sid, auth_token, from_number, to_number]):
        print("SMS alerts not configured (missing Twilio env vars). Skipping.")
        return False

    from twilio.rest import Client

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_=from_number,
        to=to_number
    )

    print("Message SID:", message.sid)

    return True


if __name__ == "__main__":
    send_sms_alert("Hidden Gem Agent Test")
