import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
COSTAR_SENDER = 'no-reply@alerts.costar.com'


def get_gmail_service():
      """Authenticate and return Gmail API service."""
      creds = None

    if os.path.exists('token.json'):
              creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
              if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
    else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                  creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
                      token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_costar_emails(service, max_results=10, after_date=None):
      """Fetch CoStar alert emails."""
    query = f'from:{COSTAR_SENDER}'
    if after_date:
              query += f' after:{after_date}'

    results = service.users().messages().list(
              userId='me',
              q=query,
              maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    emails = []

    for msg in messages:
              email_data = service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='full'
              ).execute()
              emails.append(email_data)

    return emails


def get_email_html(email_data):
      """Extract HTML body from email."""
    payload = email_data.get('payload', {})

    if 'parts' in payload:
              for part in payload['parts']:
                            if part.get('mimeType') == 'text/html':
                                              data = part['body'].get('data', '')
                                              return base64.urlsafe_b64decode(data).decode('utf-8')
                                          if 'parts' in part:
                                                            for subpart in part['parts']:
                                                                                  if subpart.get('mimeType') == 'text/html':
                                                                                                            data = subpart['body'].get('data', '')
                                                                                                            return base64.urlsafe_b64decode(data).decode('utf-8')

                                                                  if payload.get('mimeType') == 'text/html':
                                                                            data = payload['body'].get('data', '')
                                                                            return base64.urlsafe_b64decode(data).decode('utf-8')

                                                return None


def get_email_date(email_data):
      """Extract email date from headers."""
    headers = email_data.get('payload', {}).get('headers', [])
    for header in headers:
              if header['name'].lower() == 'date':
                            return header['value']
                    return None
