from later.rest import Client

account_sid = "AC9e6b34bd95ec2e5e05a2cb6a8dfd38a8"
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

message = client.messages.create(
  body="Hello from Twilio",
  from_="+13149882661",
  to="+918961675822"
)

print(message.sid)