import base64
from email.message import EmailMessage
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


creds = Credentials.from_authorized_user_file("token.json")
service = build("gmail", "v1", credentials=creds)


def send_email(recipent, subject, body, from_email="derkahlehorst@gmail.com"):
    msg = EmailMessage()
    msg["to"] = recipent
    msg["from"] = from_email
    msg["subject"] = subject
    msg.set_content(body)
    try:
        message = service.users().messages().send(userId="me", body={"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}).execute()
        return True, message
    except HttpError as error:
        return False, error
    
def move_email_to_archive(email_id):
    try:
        message = service.users().messages().modify(userId="me", id=email_id, body={"addLabelIds": ["Label_4322346357244942836"]}).execute()
        return True, message
    except HttpError as error:
        return False, error
    