from twilio.rest import Client

# Your Twilio Account SID and Auth Token
account_sid = 'ACd18540ad194a655bf4112842c3ef5be4'
auth_token = '5e7a7e4b68ca646b2892c163f2ac518f'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Your mobile phone number and Twilio phone number
to_phone_number = '+16124325527'
from_phone_number = '+18335320637'

# Message to send
message = 'Hello, Dana. This is Ron from Airport Hilton. Are you available Friday, Sept 20  at 8:00 AM?'

# Send the message
message = client.messages.create(
    body=message,
    from_=from_phone_number,
    to=to_phone_number
)

# Print the message SID to confirm it was sent
print(f"Message sent with SID: {message.sid}")

