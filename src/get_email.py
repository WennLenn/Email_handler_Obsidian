import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

SCOPES = ["https://mail.google.com/"]

creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
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

    try:
        # get headers (subject, sender,body)
        if "parts" in email["payload"]:
            data = email["payload"]["parts"][0]["body"]["data"]
        else:
            data = email["payload"]["body"]["data"]
    except KeyError:
        body = "Could not parse body"

    headers = email["payload"]["headers"]
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
    body = base64.urlsafe_b64decode(data).decode("utf-8")
    
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print(f"body: {body}")
    print("---")


    #*************************#
    #*****File handling*******#
    #*************************#
    path = {
        "pc": [rf"C:\Users\schaa\OneDrive\Desktop\Obsidian\Git_hub_folder\Email_handler\emails\{subject}.md", rf"C:\Users\schaa\OneDrive\Desktop\Obsidian\Git_hub_folder\Email_handler\Email_list.md"],
        "laptop": [rf"C:\Users\Lennard\Desktop\DnD\Obsidian\Obsidian_saves\Email_handler\emails\{subject}.md", rf"C:\Users\Lennard\Desktop\DnD\Obsidian\Obsidian_saves\Email_handler\Email_list.md"]
    }

    device = input("please enter your current device")

    try:
        with open(path[device][0], "x") as f:
            f.write(f"Written by: {sender}\n")
            f.write(f"## Content\n")
            f.write(body)

        with open(path[device][1], "r") as f:
            content = f.read()

        with open(path[device][1], "w") as f:
            new_item = f"- [ ] [[{subject}]]\n"
            content = content.replace("%% kanban:settings", new_item + "%% kanban:settings")
            f.write(content)

    except FileExistsError:
        print("file already exists")