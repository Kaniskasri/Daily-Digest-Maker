"""WhatsApp message collector (placeholder)."""
import logging
from datetime import datetime, timedelta
from typing import List
from collectors.base import MessageCollector
from models import Message


class WhatsAppCollector(MessageCollector):
    """Placeholder collector for WhatsApp messages."""
    
    def __init__(self):
        """Initialize WhatsApp collector."""
        self.logger = logging.getLogger(__name__)
    
    def get_source_name(self) -> str:
        """Get source name."""
        return "whatsapp"
    
    def collect(self) -> List[Message]:
        """
        Collect WhatsApp messages (placeholder implementation).
        
        Returns mock data for demonstration purposes.
        """
        self.logger.info("WhatsApp collection using placeholder data (not yet implemented)")
        
        # Return mock data
        mock_messages = [
            Message(
                source="whatsapp",
                sender="John Doe",
                sender_detail="+1234567890",
                content="Hey, can we reschedule our meeting?",
                timestamp=datetime.now() - timedelta(hours=2),
                message_type="chat"
            ),
            Message(
                source="whatsapp",
                sender="Jane Smith",
                sender_detail="+0987654321",
                content="Thanks for the update!",
                timestamp=datetime.now() - timedelta(hours=5),
                message_type="chat"
            )
        ]
        
        self.logger.info(f"Returning {len(mock_messages)} mock WhatsApp messages")
        return mock_messages
