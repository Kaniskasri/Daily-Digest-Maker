"""Data models for the Daily Digest Maker."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Message:
    """Represents a message from any platform."""
    source: str          # "slack", "gmail", "whatsapp"
    sender: str          # Sender name or email
    sender_detail: str   # Channel name, email address, or phone number
    content: str         # Message content or email subject
    timestamp: datetime  # When the message was sent
    message_type: str    # "channel", "direct", "email", "chat"
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'Message':
        """Create message from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return Message(**data)


@dataclass
class DigestData:
    """Container for digest data."""
    messages_by_source: Dict[str, List[Message]]
    total_count: int
    generation_time: datetime
    
    def get_source_count(self, source: str) -> int:
        """Get count of messages for a specific source."""
        return len(self.messages_by_source.get(source, []))
    
    def get_all_messages_sorted(self) -> List[Message]:
        """Get all messages sorted by timestamp descending."""
        all_messages = []
        for messages in self.messages_by_source.values():
            all_messages.extend(messages)
        return sorted(all_messages, key=lambda m: m.timestamp, reverse=True)


@dataclass
class SMTPConfig:
    """SMTP configuration."""
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True


@dataclass
class AppConfig:
    """Application configuration."""
    slack_token: Optional[str]
    gmail_credentials_path: Optional[str]
    gmail_token_path: str
    smtp: SMTPConfig
    recipient_email: str
    schedule_time: str = "20:00"
    log_level: str = "INFO"
