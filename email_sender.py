"""Email sender for delivering digests."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
from models import SMTPConfig
from utils.retry import retry_with_backoff


class EmailSender:
    """Sends digest emails via SMTP."""
    
    def __init__(self, smtp_config: SMTPConfig, recipient_email: str):
        """
        Initialize email sender.
        
        Args:
            smtp_config: SMTP configuration
            recipient_email: Recipient email address
        """
        self.smtp_config = smtp_config
        self.recipient_email = recipient_email
        self.logger = logging.getLogger(__name__)
    
    def _create_multipart_message(
        self,
        subject: str,
        plain_text: str,
        html: str,
        from_email: Optional[str] = None
    ) -> MIMEMultipart:
        """Create multipart email message."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email or self.smtp_config.username
        msg['To'] = self.recipient_email
        
        # Attach plain text and HTML parts
        part1 = MIMEText(plain_text, 'plain', 'utf-8')
        part2 = MIMEText(html, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    @retry_with_backoff(max_attempts=3, initial_delay=2.0)
    def _send_email(self, msg: MIMEMultipart) -> bool:
        """Send email via SMTP."""
        try:
            # Connect to SMTP server
            if self.smtp_config.use_tls:
                server = smtplib.SMTP(self.smtp_config.host, self.smtp_config.port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_config.host, self.smtp_config.port)
            
            # Login
            server.login(self.smtp_config.username, self.smtp_config.password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {e}")
            raise
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise
    
    def send_digest(self, plain_text: str, html: str, message_count: int) -> bool:
        """
        Send digest email.
        
        Args:
            plain_text: Plain text version of digest
            html: HTML version of digest
            message_count: Total number of messages in digest
        
        Returns:
            True if email sent successfully
        """
        try:
            # Create subject line
            today = datetime.now().strftime("%B %d, %Y")
            subject = f"Daily Digest - {today} - {message_count} notifications"
            
            self.logger.info(f"Sending digest email to {self.recipient_email}")
            
            # Create message
            msg = self._create_multipart_message(subject, plain_text, html)
            
            # Send email
            self._send_email(msg)
            
            self.logger.info(f"Digest email sent successfully at {datetime.now().isoformat()}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send digest email: {e}")
            raise
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification email.
        
        Args:
            error_message: Error message to include
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = f"Daily Digest Error - {datetime.now().strftime('%B %d, %Y')}"
            
            plain_text = f"""
Daily Digest Maker Error

An error occurred while generating your daily digest:

{error_message}

Please check the logs for more details.

Time: {datetime.now().isoformat()}
"""
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .error-box {{ 
            background-color: #fee; 
            border: 2px solid #c00; 
            padding: 20px; 
            border-radius: 5px; 
        }}
        h1 {{ color: #c00; }}
    </style>
</head>
<body>
    <div class="error-box">
        <h1>Daily Digest Maker Error</h1>
        <p>An error occurred while generating your daily digest:</p>
        <pre>{error_message}</pre>
        <p>Please check the logs for more details.</p>
        <p><small>Time: {datetime.now().isoformat()}</small></p>
    </div>
</body>
</html>
"""
            
            self.logger.info("Sending error notification email")
            
            msg = self._create_multipart_message(subject, plain_text, html)
            self._send_email(msg)
            
            self.logger.info("Error notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
            return False
