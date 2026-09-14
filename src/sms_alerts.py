from twilio.rest import Client

ACCOUNT_SID = " "
AUTH_TOKEN = " "

TWILIO_NUMBER = "+1XXXXXXXXXX"
YOUR_NUMBER = "+1XXXXXXXXXX"

client = Client(
    ACCOUNT_SID,
    AUTH_TOKEN
)

message = client.messages.create(
    body="Hidden Gem Agent Test",
    from_=TWILIO_NUMBER,
    to=YOUR_NUMBER
)

print("Message SID:", message.sid)