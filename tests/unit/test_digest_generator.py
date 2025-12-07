"""Unit tests for digest generator."""
import pytest
from datetime import datetime, timedelta
from models import Message
from digest_generator import DigestGenerator


@pytest.fixture
def sample_messages():
    """Create sample messages for testing."""
    return [
        Message(
            source="slack",
            sender="John Doe",
            sender_detail="#general",
            content="Meeting at 3 PM",
            timestamp=datetime.now() - timedelta(hours=2),
            message_type="channel"
        ),
        Message(
            source="gmail",
            sender="Jane Smith",
            sender_detail="jane@example.com",
            content="Project Update",
            timestamp=datetime.now() - timedelta(hours=1),
            message_type="email"
        ),
        Message(
            source="whatsapp",
            sender="Bob Wilson",
            sender_detail="+1234567890",
            content="Quick question",
            timestamp=datetime.now() - timedelta(minutes=30),
            message_type="chat"
        )
    ]


class TestDigestGenerator:
    """Unit tests for DigestGenerator."""
    
    def test_generate_with_messages_from_all_sources(self, sample_messages):
        """Test digest generation with messages from all sources."""
        generator = DigestGenerator()
        plain_text, html = generator.generate(sample_messages)
        
        # Check plain text
        assert "Daily Digest" in plain_text
        assert "Total Notifications: 3" in plain_text
        assert "SLACK" in plain_text
        assert "GMAIL" in plain_text
        assert "WHATSAPP" in plain_text
        
        # Check HTML
        assert "<!DOCTYPE html>" in html
        assert "Daily Digest" in html
        assert "John Doe" in html
        assert "Jane Smith" in html
        assert "Bob Wilson" in html
    
    def test_generate_with_single_source(self):
        """Test digest generation with messages from single source."""
        messages = [
            Message(
                source="slack",
                sender="User 1",
                sender_detail="#channel",
                content="Message 1",
                timestamp=datetime.now(),
                message_type="channel"
            )
        ]
        
        generator = DigestGenerator()
        plain_text, html = generator.generate(messages)
        
        assert "SLACK" in plain_text
        assert "1 messages" in plain_text or "1 message" in plain_text
        assert "User 1" in plain_text
    
    def test_generate_with_no_messages(self):
        """Test digest generation with no messages."""
        generator = DigestGenerator()
        plain_text, html = generator.generate([])
        
        assert "Daily Digest" in plain_text
        assert "Total Notifications: 0" in plain_text
        assert "No new notifications" in plain_text
        
        assert "<!DOCTYPE html>" in html
        assert "No new notifications" in html
    
    def test_html_escaping_of_special_characters(self):
        """Test that special characters are properly escaped in HTML."""
        messages = [
            Message(
                source="slack",
                sender="<script>alert('xss')</script>",
                sender_detail="#test",
                content="<b>Bold</b> & special chars",
                timestamp=datetime.now(),
                message_type="channel"
            )
        ]
        
        generator = DigestGenerator()
        plain_text, html = generator.generate(messages)
        
        # HTML should escape special characters
        assert "&lt;script&gt;" in html or "script" not in html.lower()
        assert "&lt;b&gt;" in html or "<b>Bold</b>" not in html
        assert "&amp;" in html
    
    def test_grouping_by_source(self, sample_messages):
        """Test message grouping by source."""
        generator = DigestGenerator()
        grouped = generator._group_by_source(sample_messages)
        
        assert len(grouped) == 3
        assert "slack" in grouped
        assert "gmail" in grouped
        assert "whatsapp" in grouped
        assert len(grouped["slack"]) == 1
        assert len(grouped["gmail"]) == 1
        assert len(grouped["whatsapp"]) == 1
    
    def test_sorting_by_timestamp(self, sample_messages):
        """Test message sorting by timestamp."""
        generator = DigestGenerator()
        sorted_messages = generator._sort_by_timestamp(sample_messages)
        
        # Should be in descending order (most recent first)
        assert sorted_messages[0].source == "whatsapp"  # 30 min ago
        assert sorted_messages[1].source == "gmail"     # 1 hour ago
        assert sorted_messages[2].source == "slack"     # 2 hours ago
