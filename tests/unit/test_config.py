"""Unit tests for configuration management."""
import os
import pytest
from config import Config


class TestConfig:
    """Test configuration loading and validation."""
    
    def test_load_from_environment_variables(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv('SMTP_USERNAME', 'test@example.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'testpass')
        monkeypatch.setenv('RECIPIENT_EMAIL', 'recipient@example.com')
        
        config = Config()
        smtp = config.get_smtp_settings()
        
        assert smtp.username == 'test@example.com'
        assert smtp.password == 'testpass'
        assert config.get_recipient_email() == 'recipient@example.com'
    
    def test_validation_fails_without_required_settings(self):
        """Test that validation fails when required settings are missing."""
        config = Config()
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert 'Configuration validation failed' in str(exc_info.value)
    
    def test_validation_succeeds_with_required_settings(self, monkeypatch):
        """Test that validation succeeds with all required settings."""
        monkeypatch.setenv('SMTP_USERNAME', 'test@example.com')
        monkeypatch.setenv('SMTP_PASSWORD', 'testpass')
        monkeypatch.setenv('RECIPIENT_EMAIL', 'recipient@example.com')
        
        config = Config()
        assert config.validate() is True
    
    def test_get_slack_token(self, monkeypatch):
        """Test getting Slack token."""
        monkeypatch.setenv('SLACK_BOT_TOKEN', 'xoxb-test-token')
        
        config = Config()
        assert config.get_slack_token() == 'xoxb-test-token'
    
    def test_get_gmail_credentials_path(self, monkeypatch):
        """Test getting Gmail credentials path."""
        monkeypatch.setenv('GMAIL_CREDENTIALS_PATH', 'custom/path.json')
        
        config = Config()
        assert config.get_gmail_credentials_path() == 'custom/path.json'
    
    def test_default_schedule_time(self):
        """Test default schedule time."""
        config = Config()
        assert config.get_schedule_time() == '20:00'
    
    def test_custom_schedule_time(self, monkeypatch):
        """Test custom schedule time."""
        monkeypatch.setenv('SCHEDULE_TIME', '09:00')
        
        config = Config()
        assert config.get_schedule_time() == '09:00'
