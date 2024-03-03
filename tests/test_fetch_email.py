import unittest
from unittest.mock import MagicMock, patch

from fetch_email import GmailClient


class TestGmailClient(unittest.TestCase):

    @patch('fetch_email.build')
    def test_fetch_emails_success(self, mock_build):
        # Mock the Gmail API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the response from the Gmail API
        mock_messages = {
            'messages': [
                {'id': 'message_id_1'},
                {'id': 'message_id_2'}
            ]
        }
        mock_execute = MagicMock(return_value=mock_messages)
        mock_service.users().messages().list().execute = mock_execute

        # Initialize the GmailClient and call fetch_emails
        gmail_client = GmailClient()
        emails = gmail_client.fetch_emails(max_emails=2)

        # Assertions
        self.assertIsNotNone(emails)
        self.assertEqual(len(emails), 0)

    @patch('fetch_email.build')
    def test_fetch_emails_error(self, mock_build):
        # Mock the Gmail API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock an HTTP error response from the Gmail API
        mock_execute = MagicMock(side_effect=Exception("Mocked HTTPError"))
        mock_service.users().messages().list().execute = mock_execute

        # Initialize the GmailClient and call fetch_emails
        gmail_client = GmailClient()
        emails = gmail_client.fetch_emails(max_emails=100)

        # Assertions
        self.assertIsNone(emails)

    @patch('fetch_email.build')
    def test_fetch_emails_no_emails(self, mock_build):
        # Mock the Gmail API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the response from the Gmail API with no emails
        mock_messages = {'messages': []}
        mock_execute = MagicMock(return_value=mock_messages)
        mock_service.users().messages().list().execute = mock_execute

        # Initialize the GmailClient and call fetch_emails
        gmail_client = GmailClient()
        emails = gmail_client.fetch_emails(max_emails=100)

        # Assertions
        self.assertEqual(emails, [])


if __name__ == '__main__':
    unittest.main()
