"""Digest generator for formatting collected messages."""
import logging
from datetime import datetime
from typing import List, Dict, Tuple
from models import Message
import html


class DigestGenerator:
    """Generates formatted digests from collected messages."""
    
    def __init__(self):
        """Initialize digest generator."""
        self.logger = logging.getLogger(__name__)
    
    def _group_by_source(self, messages: List[Message]) -> Dict[str, List[Message]]:
        """Group messages by source platform."""
        grouped = {}
        for message in messages:
            if message.source not in grouped:
                grouped[message.source] = []
            grouped[message.source].append(message)
        return grouped
    
    def _sort_by_timestamp(self, messages: List[Message]) -> List[Message]:
        """Sort messages by timestamp in descending order."""
        return sorted(messages, key=lambda m: m.timestamp, reverse=True)
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp in human-readable format."""
        return timestamp.strftime("%B %d, %Y at %I:%M %p")
    
    def _generate_plain_text(self, grouped_messages: Dict[str, List[Message]]) -> str:
        """Generate plain text version of digest."""
        lines = []
        
        # Header
        today = datetime.now().strftime("%B %d, %Y")
        total_count = sum(len(msgs) for msgs in grouped_messages.values())
        
        lines.append(f"Daily Digest - {today}")
        lines.append(f"Total Notifications: {total_count}")
        lines.append("")
        
        if total_count == 0:
            lines.append("No new notifications found.")
            return "\n".join(lines)
        
        # Group by source
        source_order = ["slack", "gmail", "whatsapp"]
        for source in source_order:
            if source not in grouped_messages:
                continue
            
            messages = self._sort_by_timestamp(grouped_messages[source])
            source_name = source.upper()
            
            lines.append(f"=== {source_name} ({len(messages)} messages) ===")
            lines.append("")
            
            for msg in messages:
                lines.append(f"• {msg.sender_detail} - {msg.sender} ({self._format_timestamp(msg.timestamp)})")
                lines.append(f"  {msg.content}")
                lines.append("")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(self, grouped_messages: Dict[str, List[Message]]) -> str:
        """Generate HTML version of digest."""
        today = datetime.now().strftime("%B %d, %Y")
        total_count = sum(len(msgs) for msgs in grouped_messages.values())
        
        html_parts = []
        
        # HTML header with styling
        html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .summary {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .source-section {
            margin: 30px 0;
        }
        .source-header {
            background-color: #3498db;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .source-header.slack { background-color: #4A154B; }
        .source-header.gmail { background-color: #EA4335; }
        .source-header.whatsapp { background-color: #25D366; }
        .message {
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            background-color: #f8f9fa;
            border-radius: 0 5px 5px 0;
        }
        .message-sender {
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }
        .message-detail {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .message-content {
            margin-top: 10px;
            color: #34495e;
        }
        .message-time {
            color: #95a5a6;
            font-size: 0.85em;
            margin-top: 5px;
        }
        .no-messages {
            text-align: center;
            color: #7f8c8d;
            padding: 40px;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="container">
""")
        
        # Title and summary
        html_parts.append(f"<h1>Daily Digest - {html.escape(today)}</h1>")
        html_parts.append(f'<div class="summary">Total Notifications: <strong>{total_count}</strong></div>')
        
        if total_count == 0:
            html_parts.append('<div class="no-messages">No new notifications found.</div>')
        else:
            # Group by source
            source_order = ["slack", "gmail", "whatsapp"]
            for source in source_order:
                if source not in grouped_messages:
                    continue
                
                messages = self._sort_by_timestamp(grouped_messages[source])
                source_name = source.upper()
                
                html_parts.append(f'<div class="source-section">')
                html_parts.append(f'<div class="source-header {source}">{html.escape(source_name)} ({len(messages)} messages)</div>')
                
                for msg in messages:
                    html_parts.append('<div class="message">')
                    html_parts.append(f'<div class="message-sender">{html.escape(msg.sender)}</div>')
                    html_parts.append(f'<div class="message-detail">{html.escape(msg.sender_detail)}</div>')
                    html_parts.append(f'<div class="message-content">{html.escape(msg.content)}</div>')
                    html_parts.append(f'<div class="message-time">{html.escape(self._format_timestamp(msg.timestamp))}</div>')
                    html_parts.append('</div>')
                
                html_parts.append('</div>')
        
        # HTML footer
        html_parts.append("""
    </div>
</body>
</html>
""")
        
        return "".join(html_parts)
    
    def generate(self, messages: List[Message]) -> Tuple[str, str]:
        """
        Generate both plain text and HTML digests.
        
        Args:
            messages: List of messages to include in digest
        
        Returns:
            Tuple of (plain_text, html)
        """
        self.logger.info(f"Generating digest for {len(messages)} messages")
        
        # Group and sort messages
        grouped = self._group_by_source(messages)
        
        # Generate both formats
        plain_text = self._generate_plain_text(grouped)
        html_content = self._generate_html(grouped)
        
        self.logger.info("Digest generation complete")
        
        return plain_text, html_content
