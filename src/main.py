import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build
import base64
import json

SCOPES = ["https://mail.google.com/"]

creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("gmail", "v1", credentials=creds)

results = service.users().messages().list(userId="me", q="category:primary", labelIds=["INBOX"], maxResults=10).execute()
messages = results.get("messages", [])
print(messages)

for msg in messages:
    # Get the full email
    email = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

    # get headers (subject, sender,body)
    if "parts" in email["payload"]:
        data = email["payload"]["parts"][0]["body"]["data"]
    else:
        data = email["payload"]["body"]["data"]

    headers = email["payload"]["headers"]
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
    body = base64.urlsafe_b64decode(data).decode("utf-8")
    
    print(json.dumps(email["payload"], indent=2))
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print(f"body: {body}")
    print("---")