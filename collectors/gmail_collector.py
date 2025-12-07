"""Gmail message collector."""
import logging
import os
import base64
from datetime import datetime
from typing import List, Optional
from email.utils import parsedate_to_datetime
from collectors.base import MessageCollector
from models import Message
from utils.retry import retry_with_backoff


class GmailCollector(MessageCollector):
    """Collects unread emails from Gmail."""
    
    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize Gmail collector.
        
        Args:
            credentials_path: Path to Gmail OAuth2 credentials JSON
            token_path: Path to store/load OAuth2 token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.logger = logging.getLogger(__name__)
        self.service = None
    
    def _init_service(self):
        """Initialize Gmail API service."""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.logger.info("Refreshing Gmail token")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        self.logger.error(f"Gmail credentials not found at {self.credentials_path}")
                        raise FileNotFoundError(f"Gmail credentials not found: {self.credentials_path}")
                    
                    self.logger.info("Starting OAuth2 flow for Gmail")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            
        except ImportError:
            self.logger.error("Google API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            raise
    
    def get_source_name(self) -> str:
        """Get source name."""
        return "gmail"
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def _list_unread_messages(self) -> List[dict]:
        """List unread messages."""
        if not self.service:
            self._init_service()
        
        result = self.service.users().messages().list(
            userId='me',
            q='is:unread in:inbox',
            maxResults=50
        ).execute()
        
        return result.get('messages', [])
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def _get_message(self, msg_id: str) -> dict:
        """Get full message details."""
        if not self.service:
            self._init_service()
        
        return self.service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
    
    def _extract_header(self, headers: List[dict], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value', '')
        return ''
    
    def collect(self) -> List[Message]:
        """Collect unread emails from Gmail."""
        messages = []
        
        try:
            self.logger.info("Starting Gmail message collection")
            
            # List unread messages
            message_list = self._list_unread_messages()
            self.logger.info(f"Found {len(message_list)} unread emails")
            
            for msg_ref in message_list:
                try:
                    # Get full message
                    msg = self._get_message(msg_ref['id'])
                    
                    # Extract headers
                    headers = msg.get('payload', {}).get('headers', [])
                    subject = self._extract_header(headers, 'Subject')
                    from_header = self._extract_header(headers, 'From')
                    date_header = self._extract_header(headers, 'Date')
                    
                    # Parse sender
                    sender_name = from_header
                    sender_email = from_header
                    if '<' in from_header and '>' in from_header:
                        sender_name = from_header.split('<')[0].strip().strip('"')
                        sender_email = from_header.split('<')[1].split('>')[0].strip()
                    
                    # Parse date
                    try:
                        timestamp = parsedate_to_datetime(date_header)
                    except Exception:
                        timestamp = datetime.now()
                    
                    # Create message object
                    message = Message(
                        source="gmail",
                        sender=sender_name or sender_email,
                        sender_detail=sender_email,
                        content=subject or "(No Subject)",
                        timestamp=timestamp,
                        message_type="email"
                    )
                    messages.append(message)
                
                except Exception as e:
                    self.logger.error(f"Error processing email {msg_ref.get('id')}: {e}")
                    continue
            
            self.logger.info(f"Collected {len(messages)} emails from Gmail")
            
        except Exception as e:
            self.logger.error(f"Gmail collection failed: {e}")
            return []
        
        return messages
