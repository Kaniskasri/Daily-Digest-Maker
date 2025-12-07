"""Slack message collector."""
import logging
from datetime import datetime
from typing import List, Optional
from collectors.base import MessageCollector
from models import Message
from utils.retry import retry_with_backoff


class SlackCollector(MessageCollector):
    """Collects unread messages from Slack."""
    
    def __init__(self, token: str):
        """
        Initialize Slack collector.
        
        Args:
            token: Slack bot token
        """
        self.token = token
        self.logger = logging.getLogger(__name__)
        self.client = None
    
    def _init_client(self):
        """Initialize Slack client."""
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
            self.client = WebClient(token=self.token)
            self.SlackApiError = SlackApiError
        except ImportError:
            self.logger.error("slack_sdk not installed. Install with: pip install slack-sdk")
            raise
    
    def get_source_name(self) -> str:
        """Get source name."""
        return "slack"
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def _get_conversations(self) -> List[dict]:
        """Get list of conversations."""
        if not self.client:
            self._init_client()
        
        result = self.client.conversations_list(
            types="public_channel,private_channel,im",
            exclude_archived=True
        )
        return result.get("channels", [])
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def _get_conversation_history(self, channel_id: str, oldest: Optional[str] = None) -> List[dict]:
        """Get conversation history."""
        if not self.client:
            self._init_client()
        
        result = self.client.conversations_history(
            channel=channel_id,
            oldest=oldest or "0"
        )
        return result.get("messages", [])
    
    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def _get_user_info(self, user_id: str) -> dict:
        """Get user information."""
        if not self.client:
            self._init_client()
        
        result = self.client.users_info(user=user_id)
        return result.get("user", {})
    
    def collect(self) -> List[Message]:
        """Collect unread messages from Slack."""
        messages = []
        
        try:
            self.logger.info("Starting Slack message collection")
            
            # Get all conversations
            conversations = self._get_conversations()
            self.logger.info(f"Found {len(conversations)} Slack conversations")
            
            for conv in conversations:
                channel_id = conv.get("id")
                channel_name = conv.get("name", "Direct Message")
                is_im = conv.get("is_im", False)
                
                try:
                    # Get recent messages (last 24 hours worth)
                    history = self._get_conversation_history(channel_id)
                    
                    for msg in history:
                        # Skip bot messages and messages without text
                        if msg.get("bot_id") or not msg.get("text"):
                            continue
                        
                        user_id = msg.get("user")
                        if not user_id:
                            continue
                        
                        # Get user info
                        try:
                            user_info = self._get_user_info(user_id)
                            sender_name = user_info.get("real_name") or user_info.get("name", "Unknown")
                        except Exception as e:
                            self.logger.warning(f"Failed to get user info for {user_id}: {e}")
                            sender_name = "Unknown"
                        
                        # Create message object
                        message = Message(
                            source="slack",
                            sender=sender_name,
                            sender_detail=f"#{channel_name}" if not is_im else "Direct Message",
                            content=msg.get("text", ""),
                            timestamp=datetime.fromtimestamp(float(msg.get("ts", 0))),
                            message_type="direct" if is_im else "channel"
                        )
                        messages.append(message)
                
                except Exception as e:
                    self.logger.error(f"Error processing channel {channel_name}: {e}")
                    continue
            
            self.logger.info(f"Collected {len(messages)} messages from Slack")
            
        except Exception as e:
            self.logger.error(f"Slack collection failed: {e}")
            return []
        
        return messages
