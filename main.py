"""Main orchestrator for Daily Digest Maker."""
import sys
import logging
from typing import List
from datetime import datetime

from config import Config
from models import Message
from utils.logger import setup_logger
from collectors.slack_collector import SlackCollector
from collectors.gmail_collector import GmailCollector
from collectors.whatsapp_collector import WhatsAppCollector
from digest_generator import DigestGenerator
from email_sender import EmailSender


def collect_messages_from_all_sources(config_obj: Config, logger: logging.Logger) -> List[Message]:
    """
    Collect messages from all configured sources.
    
    Args:
        config_obj: Configuration object
        logger: Logger instance
    
    Returns:
        List of all collected messages
    """
    all_messages = []
    
    # Slack
    if config_obj.get_slack_token():
        try:
            logger.info("Collecting messages from Slack")
            slack_collector = SlackCollector(config_obj.get_slack_token())
            slack_messages = slack_collector.collect()
            all_messages.extend(slack_messages)
            logger.info(f"Collected {len(slack_messages)} messages from Slack")
        except Exception as e:
            logger.error(f"Slack collection failed: {e}")
    else:
        logger.info("Slack token not configured, skipping Slack collection")
    
    # Gmail
    if config_obj.get_gmail_credentials_path():
        try:
            logger.info("Collecting messages from Gmail")
            gmail_collector = GmailCollector(
                config_obj.get_gmail_credentials_path(),
                config_obj.get_gmail_token_path()
            )
            gmail_messages = gmail_collector.collect()
            all_messages.extend(gmail_messages)
            logger.info(f"Collected {len(gmail_messages)} messages from Gmail")
        except Exception as e:
            logger.error(f"Gmail collection failed: {e}")
    else:
        logger.info("Gmail credentials not configured, skipping Gmail collection")
    
    # WhatsApp (placeholder) - Only enabled if configured
    if config_obj.get_enable_whatsapp_placeholder():
        try:
            logger.info("Collecting messages from WhatsApp (placeholder)")
            whatsapp_collector = WhatsAppCollector()
            whatsapp_messages = whatsapp_collector.collect()
            all_messages.extend(whatsapp_messages)
            logger.info(f"Collected {len(whatsapp_messages)} messages from WhatsApp")
        except Exception as e:
            logger.error(f"WhatsApp collection failed: {e}")
    else:
        logger.info("WhatsApp collection disabled (set ENABLE_WHATSAPP_PLACEHOLDER=true to enable)")
    
    return all_messages


def main():
    """Main orchestrator function."""
    logger = None
    
    try:
        # Load configuration
        config_obj = Config('.env')
        
        # Setup logger
        logger = setup_logger('daily_digest_maker', config_obj.get_log_level())
        logger.info("=" * 60)
        logger.info("Daily Digest Maker - Starting execution")
        logger.info(f"Execution time: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        # Validate configuration
        try:
            config_obj.validate()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            sys.exit(1)
        
        # Get app config
        app_config = config_obj.get_app_config()
        
        # Collect messages from all sources
        logger.info("Starting message collection from all sources")
        all_messages = collect_messages_from_all_sources(config_obj, logger)
        logger.info(f"Total messages collected: {len(all_messages)}")
        
        # Generate digest
        logger.info("Generating digest")
        digest_generator = DigestGenerator()
        plain_text, html = digest_generator.generate(all_messages)
        
        # Send email
        logger.info("Sending digest email")
        email_sender = EmailSender(app_config.smtp, app_config.recipient_email)
        email_sender.send_digest(plain_text, html, len(all_messages))
        
        # Log success
        logger.info("=" * 60)
        logger.info("Daily Digest Maker - Execution completed successfully")
        logger.info(f"Messages processed: {len(all_messages)}")
        logger.info(f"Completion time: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
    except Exception as e:
        if logger:
            logger.error("=" * 60)
            logger.error("Daily Digest Maker - Execution failed")
            logger.error(f"Error: {e}", exc_info=True)
            logger.error("=" * 60)
            
            # Try to send error notification
            try:
                config_obj = Config('.env')
                app_config = config_obj.get_app_config()
                email_sender = EmailSender(app_config.smtp, app_config.recipient_email)
                email_sender.send_error_notification(str(e))
            except Exception as notify_error:
                logger.error(f"Failed to send error notification: {notify_error}")
        else:
            print(f"Fatal error: {e}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
