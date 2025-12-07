# Implementation Plan

- [ ] 1. Set up project structure and core data models
  - Create directory structure (collectors/, utils/, tests/, logs/, credentials/)
  - Create __init__.py files for Python packages
  - Implement Message dataclass with all required fields
  - Implement DigestData dataclass
  - Implement configuration dataclasses (SMTPConfig, AppConfig)
  - _Requirements: 8.1, 8.3_

- [ ] 1.1 Write property test for Message data integrity
  - **Property 2: Message data integrity**
  - **Validates: Requirements 1.3, 2.3, 3.2, 3.5**

- [ ] 2. Implement configuration management
  - Create config.py with Config class
  - Implement loading from environment variables
  - Implement loading from .env file using python-dotenv
  - Implement validation for required settings
  - Create .env.example with all configuration variables
  - Add .gitignore with credentials/, .env, logs/, __pycache__
  - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [ ] 2.1 Write unit tests for configuration loading
  - Test loading from environment variables
  - Test loading from config file
  - Test missing required configuration
  - Test validation logic
  - _Requirements: 9.1, 9.3_

- [ ] 3. Implement logging utilities
  - Create utils/logger.py with logging configuration
  - Implement log formatting with timestamp, level, component, message
  - Implement file logging with rotation
  - Implement credential sanitization in logs
  - _Requirements: 11.1, 11.2, 9.4_

- [ ] 3.1 Write property test for credential security in logs
  - **Property 15: Credential security in logs**
  - **Validates: Requirements 9.4**

- [ ] 4. Implement retry utilities
  - Create utils/retry.py with retry decorator
  - Implement exponential backoff logic
  - Implement retry with configurable attempts and delays
  - _Requirements: 11.4_

- [ ] 5. Implement base MessageCollector interface
  - Create collectors/base.py with MessageCollector abstract class
  - Define collect() abstract method
  - Define get_source_name() abstract method
  - _Requirements: 8.1, 8.4_

- [ ] 5.1 Write property test for interface compatibility
  - **Property 3: Interface compatibility**
  - **Validates: Requirements 8.4, 8.5**

- [ ] 5.2 Write property test for standardized return format
  - **Property 14: Standardized return format**
  - **Validates: Requirements 8.5**

- [ ] 6. Implement Slack collector
  - Create collectors/slack_collector.py
  - Implement SlackCollector class extending MessageCollector
  - Implement authentication with Slack API using slack_sdk
  - Implement conversations.list to get channels
  - Implement conversations.history to get messages
  - Implement users.info to get user display names
  - Extract message content, sender, channel, timestamp
  - Implement error handling (network, auth, rate limiting)
  - Return empty list on errors without raising exceptions
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 6.1 Write property test for message collection completeness
  - **Property 1: Message collection completeness**
  - **Validates: Requirements 1.2**

- [ ] 6.2 Write unit tests for Slack collector
  - Test successful authentication
  - Test message retrieval with mock responses
  - Test error handling (network, auth, rate limiting)
  - Test empty message handling
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [ ] 7. Implement Gmail collector
  - Create collectors/gmail_collector.py
  - Implement GmailCollector class extending MessageCollector
  - Implement OAuth2 authentication flow
  - Implement token storage and refresh logic
  - Implement users.messages.list to query unread emails
  - Implement users.messages.get to retrieve email details
  - Extract subject, sender name, sender email, timestamp
  - Implement error handling (network, auth, quota)
  - Return empty list on errors without raising exceptions
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 7.1 Write property test for API response validation
  - **Property 16: API response validation**
  - **Validates: Requirements 11.3**

- [ ] 7.2 Write unit tests for Gmail collector
  - Test OAuth2 authentication flow
  - Test token refresh logic
  - Test message retrieval with mock responses
  - Test error handling (network, auth, quota)
  - Test empty inbox handling
  - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [ ] 8. Implement WhatsApp collector placeholder
  - Create collectors/whatsapp_collector.py
  - Implement WhatsAppCollector class extending MessageCollector
  - Return mock data in Message format
  - Log placeholder status message
  - Include contact name, message preview, timestamp in mock data
  - _Requirements: 3.1, 3.2, 3.4, 3.5_

- [ ] 9. Checkpoint - Ensure all collector tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement digest generator
  - Create digest_generator.py with DigestGenerator class
  - Implement _group_by_source() to group messages by source
  - Implement _sort_by_timestamp() to sort messages descending
  - Implement _generate_plain_text() with section headers and bullets
  - Implement _generate_html() with professional styling and responsive design
  - Implement generate() to return both plain text and HTML
  - Handle empty message collections gracefully
  - Include message count per source in both formats
  - Format timestamps in human-readable format
  - Display sender name and sender_detail consistently
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 10.1 Write property test for message grouping correctness
  - **Property 4: Message grouping correctness**
  - **Validates: Requirements 4.1**

- [ ] 10.2 Write property test for timestamp ordering
  - **Property 5: Timestamp ordering**
  - **Validates: Requirements 4.2**

- [ ] 10.3 Write property test for dual format generation
  - **Property 6: Dual format generation**
  - **Validates: Requirements 4.3**

- [ ] 10.4 Write property test for digest content completeness
  - **Property 7: Digest content completeness**
  - **Validates: Requirements 4.4, 5.5**

- [ ] 10.5 Write property test for timestamp formatting consistency
  - **Property 8: Timestamp formatting consistency**
  - **Validates: Requirements 5.3**

- [ ] 10.6 Write property test for sender information structure
  - **Property 9: Sender information structure**
  - **Validates: Requirements 5.4**

- [ ] 10.7 Write property test for plain text structure
  - **Property 10: Plain text structure**
  - **Validates: Requirements 5.1**

- [ ] 10.8 Write unit tests for digest generator
  - Test digest with messages from all sources
  - Test digest with single source
  - Test digest with no messages
  - Test HTML escaping of special characters
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [ ] 11. Implement email sender
  - Create email_sender.py with EmailSender class
  - Implement SMTP connection with TLS/SSL support
  - Implement send_digest() to send multipart email (plain text + HTML)
  - Format subject line with date and notification count
  - Implement connection retry logic
  - Implement send_error_notification() for critical errors
  - Log confirmation on successful send
  - Log detailed errors and raise exception on failure
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 11.5_

- [ ] 11.1 Write property test for email multipart structure
  - **Property 11: Email multipart structure**
  - **Validates: Requirements 6.2**

- [ ] 11.2 Write property test for subject line format
  - **Property 12: Subject line format**
  - **Validates: Requirements 6.3**

- [ ] 11.3 Write unit tests for email sender
  - Test SMTP connection and authentication
  - Test email composition with multipart content
  - Test email sending failure handling
  - Test retry logic
  - _Requirements: 6.1, 6.2, 6.5_

- [ ] 12. Implement orchestrator
  - Create main.py with main() function
  - Load configuration and validate
  - Initialize logger
  - Initialize all collectors (Slack, Gmail, WhatsApp)
  - Execute all collectors with individual error handling
  - Collect all messages into single list
  - Initialize DigestGenerator and generate digest
  - Initialize EmailSender and send digest
  - Log execution summary with success/failure status
  - Send error notification email on critical failures
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.3_

- [ ] 12.1 Write property test for error resilience
  - **Property 13: Error resilience**
  - **Validates: Requirements 7.4**

- [ ] 12.2 Write unit tests for orchestrator
  - Test complete workflow with all components
  - Test workflow with collector failures
  - Test workflow with email sending failure
  - Test error notification sending
  - _Requirements: 7.3, 7.4, 7.5_

- [ ] 13. Create requirements.txt
  - Add slack-sdk
  - Add google-auth, google-auth-oauthlib, google-api-python-client
  - Add python-dotenv
  - Add pytz
  - Add pytest
  - Add hypothesis
  - Pin versions for reproducibility
  - _Requirements: 10.3_

- [ ] 14. Create README documentation
  - Write project overview and features list
  - Document setup instructions (Python version, virtual environment)
  - Document API credential setup for Slack (bot token creation)
  - Document API credential setup for Gmail (OAuth2 credentials)
  - Document SMTP configuration for different providers
  - Document environment variables and .env file setup
  - Document scheduler setup (cron examples for Linux/Mac, Task Scheduler for Windows)
  - Include example cron job configuration for 8 PM daily execution
  - Document how to run the system manually for testing
  - Include troubleshooting section
  - Add section explaining how Kiro accelerated development
  - _Requirements: 10.1, 10.2, 10.4, 10.5_

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
