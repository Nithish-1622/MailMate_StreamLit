import imaplib
import email
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import mimetypes
import pandas as pd
from bs4 import BeautifulSoup
import ssl
from config.config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class EmailDataLoader:
    def __init__(self):
        self.imap_server = Config.IMAP_SERVER
        self.imap_port = Config.IMAP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.max_emails = Config.MAX_EMAILS_FETCH
        self.connection = None  
    def connect(self) -> bool:
        try:
            context = ssl.create_default_context()
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, ssl_context=context)
            self.connection.login(self.email_address, self.email_password)
            logger.info("Successfully connected to email server")
            return True            
        except Exception as e:
            logger.error(f"Failed to connect to email server: {str(e)}")
            return False   
    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
                logger.info("Disconnected from email server")
            except:
                pass   
    def fetch_recent_emails(self, days: int = 7, folder: str = 'INBOX') -> List[Dict[str, Any]]:
        if not self.connection:
            if not self.connect():
                return []
        try:
            self.connection.select(folder)
            since_date = datetime.now() - timedelta(days=days)
            date_str = since_date.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE "{date_str}")'
            typ, data = self.connection.search(None, search_criteria)
            if typ != 'OK':
                logger.error("Failed to search emails")
                return []
            email_ids = data[0].split()
            if len(email_ids) > self.max_emails:
                email_ids = email_ids[-self.max_emails:]
            emails = []
            for email_id in email_ids:
                email_data = self._fetch_single_email(email_id)
                if email_data:
                    emails.append(email_data)
            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
    def _fetch_single_email(self, email_id: bytes) -> Dict[str, Any]:
        try:
            typ, data = self.connection.fetch(email_id, '(RFC822)')
            if typ != 'OK':
                return None
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            sender = self._decode_header(email_message.get('From', ''))
            subject = self._decode_header(email_message.get('Subject', ''))
            date_str = email_message.get('Date', '')
            try:
                timestamp = email.utils.parsedate_to_datetime(date_str)
            except:
                timestamp = datetime.now()
            body = self._extract_body(email_message)
            cleaned_body = self._preprocess_body(body)
            return {
                'id': email_id.decode(),
                'sender': sender,
                'subject': subject,
                'body': cleaned_body,
                'raw_body': body,
                'timestamp': timestamp,
                'folder': 'INBOX'
            }
        except Exception as e:
            logger.error(f"Error parsing email {email_id}: {str(e)}")
            return None
    def _decode_header(self, header: str) -> str:
        try:
            decoded_parts = email.header.decode_header(header)
            decoded_header = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        part = part.decode(encoding)
                    else:
                        part = part.decode('utf-8', errors='ignore')
                decoded_header += part
            return decoded_header.strip()
        except:
            return header
    def _extract_body(self, email_message) -> str:
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    continue
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        continue
                elif content_type == "text/html" and not body:
                    try:
                        html_body = part.get_payload(decode=True).decode()
                        body = self._html_to_text(html_body)
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
                if email_message.get_content_type() == "text/html":
                    body = self._html_to_text(body)
            except:
                body = str(email_message.get_payload())
        return body
    def _html_to_text(self, html: str) -> str:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        except:
            return html
    def _preprocess_body(self, body: str) -> str:
        if not body:
            return ""
        signature_patterns = [
            r'--\s*\n.*',
            r'Best regards.*',
            r'Sincerely.*',
            r'Thanks.*\n.*',
            r'Sent from my.*',
            r'This email.*confidential.*',
            r'CONFIDENTIALITY NOTICE.*',
            r'The information.*confidential.*'
        ]
        cleaned_body = body
        for pattern in signature_patterns:
            cleaned_body = re.sub(pattern, '', cleaned_body, flags=re.IGNORECASE | re.DOTALL)
        cleaned_body = re.sub(r'\n\s*\n', '\n\n', cleaned_body)
        cleaned_body = re.sub(r'\s+', ' ', cleaned_body)
        cleaned_body = re.sub(r'^>.*$', '', cleaned_body, flags=re.MULTILINE)
        cleaned_body = re.sub(r'On.*wrote:.*', '', cleaned_body, flags=re.DOTALL)
        return cleaned_body.strip()
    def get_email_stats(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not emails:
            return {}
        df = pd.DataFrame(emails)
        stats = {
            'total_emails': len(emails),
            'date_range': {
                'start': df['timestamp'].min().strftime('%Y-%m-%d'),
                'end': df['timestamp'].max().strftime('%Y-%m-%d')
            },
            'unique_senders': df['sender'].nunique(),
            'top_senders': df['sender'].value_counts().head(5).to_dict()
        }
        return stats
def test_email_loader():
    loader = EmailDataLoader()
    if loader.connect():
        emails = loader.fetch_recent_emails(days=1)
        print(f"Fetched {len(emails)} emails")
        if emails:
            print("\nFirst email preview:")
            first_email = emails[0]
            print(f"From: {first_email['sender']}")
            print(f"Subject: {first_email['subject']}")
            print(f"Body preview: {first_email['body'][:200]}...")
        loader.disconnect()
    else:
        print("Failed to connect to email server")
if __name__ == "__main__":
    test_email_loader()