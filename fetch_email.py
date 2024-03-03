import logging
import os.path
import pickle
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.dialects.postgresql import insert

from db.engine import Session, engine
from db.models import Email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class GmailConstants:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.pickle'


class GmailClient:
    """
    A client class for interfacing with the Gmail API. Handles authentication with Google's OAuth and provides
    functionality to fetch emails from the Gmail account.
    """

    def __init__(self):
        """
        Initialize the GmailClient and authenticate the Gmail API.
        """
        self.service = self.authenticate_gmail()

    @staticmethod
    def authenticate_gmail():
        """
        Handle OAuth authentication with the Gmail API.
        :return:
            service: An authorized Gmail API service instance.
        """
        creds = None
        if os.path.exists(GmailConstants.TOKEN_FILE):
            with open(GmailConstants.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(GmailConstants.CREDENTIALS_FILE, GmailConstants.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(GmailConstants.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def fetch_emails(self, max_emails=100):
        """
        Fetch a specified number of emails from the user's Gmail inbox.
        :param max_emails: The maximum number of emails to fetch. This field defaults to 100. Max is 500.
        :return:
            messages: A list of email messages or None if an error occurs.
        """
        try:
            # Call the Gmail API to fetch a specified number of emails from INBOX
            max_emails = min(max_emails, 500)

            results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_emails)
            message_ids = results.execute().get('messages', [])

            def callback(request_id, response, exception):
                if exception is not None:
                    logging.error(f'An error occurred: {exception}')
                else:
                    headers = {header['name']: header['value'] for header in
                               response.get('payload', {}).get('headers', [])}

                    parsed_date = parsedate_to_datetime(headers.get('Date'))
                    emails_info.append({
                        'id': response['id'],
                        'from_address': headers.get('From', ''),
                        'to_address': headers.get('To', ''),
                        'subject': headers.get('Subject', ''),
                        'date_received': parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                    })

            emails_info = []
            batch = self.service.new_batch_http_request(callback=callback)
            for message_id in message_ids:
                batch.add(self.service.users().messages().get(userId='me', id=message_id['id']))

            batch.execute()

            return emails_info

        except HttpError as error:
            logging.error(f'An error occurred: {error}')  # pragma: no cover
            return None  # pragma: no cover

        except Exception as e:
            logging.error(f'Error - {e}')
            return None


def main():
    try:  # pragma: no cover
        client = GmailClient()
        session = Session()

        emails = client.fetch_emails(max_emails=100)
        if emails:
            with engine.begin() as connection:
                stmt = insert(Email).values(emails)
                upsert_stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={
                        'from_address': stmt.excluded.from_address,
                        'to_address': stmt.excluded.to_address,
                        'subject': stmt.excluded.subject,
                        'date_received': stmt.excluded.date_received
                    }
                )
                connection.execute(upsert_stmt)
                logging.info("Bulk upsert completed successfully.")
        else:
            logging.info('No emails found.')

    except HttpError as error:  # pragma: no cover
        logging.error(f'An HTTP error occurred: {error}')
    except Exception as e:  # pragma: no cover
        logging.error(f'An unexpected error occurred: {e}')
        session.rollback()
    finally:  # pragma: no cover
        session.close()


if __name__ == '__main__':
    main()  # pragma: no cover
