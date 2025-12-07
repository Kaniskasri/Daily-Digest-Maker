"""Base interface for message collectors."""
from abc import ABC, abstractmethod
from typing import List
from models import Message


class MessageCollector(ABC):
    """Abstract base class for all message collectors."""
    
    @abstractmethod
    def collect(self) -> List[Message]:
        """
        Collect messages from the platform.
        
        Returns:
            List of Message objects. Returns empty list on error.
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of the message source.
        
        Returns:
            Source name (e.g., "slack", "gmail", "whatsapp")
        """
        pass
