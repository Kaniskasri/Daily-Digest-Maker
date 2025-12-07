"""Property-based tests for Message data model."""
import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from models import Message


# Custom strategies for generating test data
@st.composite
def message_strategy(draw):
    """Generate random Message objects."""
    sources = ["slack", "gmail", "whatsapp"]
    message_types = ["channel", "direct", "email", "chat"]
    
    return Message(
        source=draw(st.sampled_from(sources)),
        sender=draw(st.text(min_size=1, max_size=100)),
        sender_detail=draw(st.text(min_size=1, max_size=100)),
        content=draw(st.text(min_size=1, max_size=500)),
        timestamp=draw(st.datetimes(
            min_value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )),
        message_type=draw(st.sampled_from(message_types))
    )


class TestMessageProperties:
    """Property-based tests for Message model."""
    
    @given(message_strategy())
    def test_message_data_integrity(self, message):
        """
        Feature: daily-digest-maker, Property 2: Message data integrity
        
        For any collected message, the Message object should contain all 
        required fields with non-null values.
        
        Validates: Requirements 1.3, 2.3, 3.2, 3.5
        """
        # All required fields must be present and non-null
        assert message.source is not None
        assert message.sender is not None
        assert message.sender_detail is not None
        assert message.content is not None
        assert message.timestamp is not None
        assert message.message_type is not None
        
        # Fields must have correct types
        assert isinstance(message.source, str)
        assert isinstance(message.sender, str)
        assert isinstance(message.sender_detail, str)
        assert isinstance(message.content, str)
        assert isinstance(message.timestamp, datetime)
        assert isinstance(message.message_type, str)
        
        # String fields must not be empty
        assert len(message.source) > 0
        assert len(message.sender) > 0
        assert len(message.sender_detail) > 0
        assert len(message.content) > 0
        assert len(message.message_type) > 0
    
    @given(message_strategy())
    def test_message_serialization_round_trip(self, message):
        """
        Test that messages can be serialized and deserialized.
        
        For any message, converting to dict and back should preserve all data.
        """
        # Convert to dict
        message_dict = message.to_dict()
        
        # Convert back to Message
        restored_message = Message.from_dict(message_dict)
        
        # All fields should match
        assert restored_message.source == message.source
        assert restored_message.sender == message.sender
        assert restored_message.sender_detail == message.sender_detail
        assert restored_message.content == message.content
        assert restored_message.message_type == message.message_type
        
        # Timestamps should be equal (within microsecond precision)
        assert abs((restored_message.timestamp - message.timestamp).total_seconds()) < 0.001
