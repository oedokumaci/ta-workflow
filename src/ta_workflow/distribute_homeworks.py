import base64
import email
from datetime import datetime
from pathlib import Path
from urllib.request import Request

from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

# Set the folder name, Gmail API credentials file path, and output folder path
folder_name = "Your folder name"
credentials_path = Path("path/to/credentials.json")
output_folder_path = Path("path/to/output/folder")


# Define a function to retrieve the Gmail API service object
def get_gmail_service():
    creds = None
    if (token := output_folder_path / "token.json").exists():
        creds = Credentials.from_authorized_user_file(
            token, ["https://www.googleapis.com/auth/gmail.readonly"]
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, ["https://www.googleapis.com/auth/gmail.readonly"]
            )
            creds = flow.run_local_server(port=0)
        with open(token, "w") as token_file:
            token_file.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    return service


# Define a function to retrieve a list of message IDs in the specified folder
def get_message_ids(service):
    try:
        response = (
            service.users()
            .messages()
            .list(userId="me", q=f"in:{folder_name}")
            .execute()
        )
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])
        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId="me", q=f"in:{folder_name}", pageToken=page_token)
                .execute()
            )
            if "messages" in response:
                messages.extend(response["messages"])
        message_ids = []
        for message in messages:
            message_ids.append(message["id"])
        return message_ids
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


# Define a function to retrieve the specified message and parse the attachments
def get_message_attachments(service, message_id):
    try:
        message = service.users().messages().get(userId="me", id=message_id).execute()
        msg = email.message_from_string(message["payload"]["headers"][0]["value"])
        sender = msg["From"].split()[-1].strip("<>")
        date = datetime.fromtimestamp(int(message["internalDate"]) / 1000).strftime(
            "%Y-%m-%d %H-%M-%S"
        )
        for part in message["payload"]["parts"]:
            if part["filename"]:
                filename = f"{date} {sender} {folder_name} {part['filename']}"
                data = part["body"]["data"]
                file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
                with open(output_folder_path / filename, "wb") as f:
                    f.write(file_data)
    except HttpError as error:
        print(f"An error occurred: {error}")


# Retrieve the Gmail API service object
service = get_gmail_service()

# Retrieve the list of message IDs in the specified folder
message_ids = get_message_ids(service)

# Iterate through each message ID and download the attachments
if message_ids:
    for message_id in message_ids:
        get_message_attachments(service, message_id)
    print("Attachments downloaded successfully.")
else:
    print("No messages found in the specified folder.")
