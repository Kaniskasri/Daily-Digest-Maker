"""Property-based tests for digest generation."""
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime, timedelta
from models import Message
from digest_generator import DigestGenerator


@st.composite
def message_list_strategy(draw, min_size=0, max_size=20):
    """Generate list of random messages."""
    sources = ["slack", "gmail", "whatsapp"]
    message_types = ["channel", "direct", "email", "chat"]
    
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    messages = []
    
    for _ in range(size):
        message = Message(
            source=draw(st.sampled_from(sources)),
            sender=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',)))),
            sender_detail=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',)))),
            content=draw(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))),
            timestamp=draw(st.datetimes(
                min_value=datetime.now() - timedelta(days=7),
                max_value=datetime.now()
            )),
            message_type=draw(st.sampled_from(message_types))
        )
        messages.append(message)
    
    return messages


class TestDigestProperties:
    """Property-based tests for digest generation."""
    
    @given(message_list_strategy(min_size=1, max_size=20))
    def test_message_grouping_correctness(self, messages):
        """
        Feature: daily-digest-maker, Property 4: Message grouping correctness
        
        For any collection of messages from multiple sources, grouping by source 
        should result in each message appearing in exactly one group corresponding 
        to its source field.
        
        Validates: Requirements 4.1
        """
        generator = DigestGenerator()
        grouped = generator._group_by_source(messages)
        
        # Count total messages in groups
        total_in_groups = sum(len(msgs) for msgs in grouped.values())
        assert total_in_groups == len(messages)
        
        # Each message should appear in exactly one group
        for message in messages:
            assert message.source in grouped
            assert message in grouped[message.source]
            
            # Message should not appear in other groups
            for source, group_messages in grouped.items():
                if source == message.source:
                    assert message in group_messages
                else:
                    assert message not in group_messages
    
    @given(message_list_strategy(min_size=2, max_size=20))
    def test_timestamp_ordering(self, messages):
        """
        Feature: daily-digest-maker, Property 5: Timestamp ordering
        
        For any group of messages, sorting by timestamp in descending order 
        should result in messages ordered from most recent to oldest.
        
        Validates: Requirements 4.2
        """
        generator = DigestGenerator()
        sorted_messages = generator._sort_by_timestamp(messages)
        
        # Check that messages are in descending order
        for i in range(len(sorted_messages) - 1):
            assert sorted_messages[i].timestamp >= sorted_messages[i + 1].timestamp
    
    @given(message_list_strategy(min_size=0, max_size=20))
    def test_dual_format_generation(self, messages):
        """
        Feature: daily-digest-maker, Property 6: Dual format generation
        
        For any collection of messages, the digest generator should produce 
        both a plain text string and an HTML string, both non-empty when 
        messages exist.
        
        Validates: Requirements 4.3
        """
        generator = DigestGenerator()
        plain_text, html = generator.generate(messages)
        
        # Both should be strings
        assert isinstance(plain_text, str)
        assert isinstance(html, str)
        
        # Both should be non-empty
        assert len(plain_text) > 0
        assert len(html) > 0
        
        # HTML should contain HTML tags
        assert '<html>' in html or '<!DOCTYPE html>' in html
    
    @given(message_list_strategy(min_size=1, max_size=20))
    def test_digest_content_completeness(self, messages):
        """
        Feature: daily-digest-maker, Property 7: Digest content completeness
        
        For any collection of messages, the generated digest should include 
        the message count per source, sender information, and content preview 
        for each message.
        
        Validates: Requirements 4.4, 5.5
        """
        generator = DigestGenerator()
        plain_text, html = generator.generate(messages)
        
        # Group messages by source for verification
        sources = {}
        for msg in messages:
            sources[msg.source] = sources.get(msg.source, 0) + 1
        
        # Check that each source count appears in both formats
        for source, count in sources.items():
            source_upper = source.upper()
            # Plain text should contain source name and count
            assert source_upper in plain_text
            assert str(count) in plain_text
            
            # HTML should contain source name
            assert source_upper in html or source in html
        
        # Check that sender information appears
        for msg in messages:
            # At least one format should contain sender info
            assert msg.sender in plain_text or msg.sender in html
    
    @given(message_list_strategy(min_size=1, max_size=10))
    def test_timestamp_formatting_consistency(self, messages):
        """
        Feature: daily-digest-maker, Property 8: Timestamp formatting consistency
        
        For any message timestamp, the formatted timestamp in the digest should 
        include both date and time components in a human-readable format.
        
        Validates: Requirements 5.3
        """
        generator = DigestGenerator()
        plain_text, html = generator.generate(messages)
        
        # Check that timestamps are formatted with date and time
        for msg in messages:
            formatted = generator._format_timestamp(msg.timestamp)
            
            # Should contain month name or number
            assert any(month in formatted for month in [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]) or any(str(i) in formatted for i in range(1, 13))
            
            # Should contain year
            assert str(msg.timestamp.year) in formatted
            
            # Should contain time indicator (AM/PM or colon for time)
            assert 'AM' in formatted or 'PM' in formatted or ':' in formatted
    
    @given(message_list_strategy(min_size=1, max_size=10))
    def test_plain_text_structure(self, messages):
        """
        Feature: daily-digest-maker, Property 10: Plain text structure
        
        For any generated plain text digest, it should contain section headers 
        for each source with messages, and use consistent formatting.
        
        Validates: Requirements 5.1
        """
        generator = DigestGenerator()
        plain_text, html = generator.generate(messages)
        
        # Get unique sources
        sources = set(msg.source for msg in messages)
        
        # Check for section headers
        for source in sources:
            source_upper = source.upper()
            assert source_upper in plain_text
        
        # Check for consistent formatting (bullets or dashes)
        assert '•' in plain_text or '-' in plain_text or '*' in plain_text
        
        # Check for title
        assert 'Daily Digest' in plain_text
        assert 'Total Notifications' in plain_text
