"""Configuration management for Daily Digest Maker."""
import os
from typing import Optional
from models import SMTPConfig, AppConfig


class Config:
    """Manages configuration from environment variables and files."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration."""
        self.config_file = config_file
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        if self.config_file and os.path.exists(self.config_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(self.config_file)
            except ImportError:
                pass  # python-dotenv not installed
    
    def get_slack_token(self) -> Optional[str]:
        """Get Slack bot token."""
        return os.getenv('SLACK_BOT_TOKEN')
    
    def get_gmail_credentials_path(self) -> Optional[str]:
        """Get path to Gmail credentials file."""
        return os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials/gmail_credentials.json')
    
    def get_gmail_token_path(self) -> str:
        """Get path to Gmail token file."""
        return os.getenv('GMAIL_TOKEN_PATH', 'credentials/gmail_token.json')
    
    def get_smtp_settings(self) -> SMTPConfig:
        """Get SMTP configuration."""
        return SMTPConfig(
            host=os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            port=int(os.getenv('SMTP_PORT', '587')),
            username=os.getenv('SMTP_USERNAME', ''),
            password=os.getenv('SMTP_PASSWORD', ''),
            use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        )
    
    def get_recipient_email(self) -> str:
        """Get recipient email address."""
        return os.getenv('RECIPIENT_EMAIL', '')
    
    def get_schedule_time(self) -> str:
        """Get scheduled execution time."""
        return os.getenv('SCHEDULE_TIME', '20:00')
    
    def get_log_level(self) -> str:
        """Get logging level."""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    def get_enable_whatsapp_placeholder(self) -> bool:
        """Get whether to enable WhatsApp placeholder messages."""
        return os.getenv('ENABLE_WHATSAPP_PLACEHOLDER', 'false').lower() == 'true'
    
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        errors = []
        
        smtp = self.get_smtp_settings()
        if not smtp.username:
            errors.append("SMTP_USERNAME is required")
        if not smtp.password:
            errors.append("SMTP_PASSWORD is required")
        
        if not self.get_recipient_email():
            errors.append("RECIPIENT_EMAIL is required")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True
    
    def get_app_config(self) -> AppConfig:
        """Get complete application configuration."""
        return AppConfig(
            slack_token=self.get_slack_token(),
            gmail_credentials_path=self.get_gmail_credentials_path(),
            gmail_token_path=self.get_gmail_token_path(),
            smtp=self.get_smtp_settings(),
            recipient_email=self.get_recipient_email(),
            schedule_time=self.get_schedule_time(),
            log_level=self.get_log_level()
        )
