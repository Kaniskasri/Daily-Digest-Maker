# Design Document

## Overview

The Daily Digest Maker (DDM) is a Python-based automation system that consolidates notifications from multiple communication platforms into a single daily email digest. The system follows a modular architecture with independent collectors for each platform (Slack, Gmail, WhatsApp), a centralized digest generator, an email sender, and an orchestrator that coordinates the entire workflow.

The system is designed to run as a scheduled task (via cron or similar scheduler) and executes the complete workflow autonomously. Each component is isolated with well-defined interfaces, making the system maintainable and extensible.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Scheduler                             │
│                    (Cron/Task Scheduler)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                            │
│                   (main.py)                                  │
└─────┬──────────┬──────────┬──────────┬─────────────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
│  Slack   │ │  Gmail   │ │ WhatsApp │ │ Config Manager   │
│Collector │ │Collector │ │Collector │ │                  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────────────┘
     │            │            │
     └────────────┴────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Digest Generator│
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Email Sender   │
         └─────────────────┘
```

### Component Interaction Flow

1. **Scheduler** triggers the Orchestrator at the configured time (8 PM by default)
2. **Orchestrator** loads configuration and initializes all components
3. **Message Collectors** (Slack, Gmail, WhatsApp) execute in parallel or sequence, each returning a standardized message collection
4. **Digest Generator** receives all collected messages, groups them by source, and formats them into plain text and HTML
5. **Email Sender** delivers the formatted digest via SMTP
6. **Orchestrator** logs the execution summary and handles any errors

## Components and Interfaces

### 1. Configuration Manager (`config.py`)

**Purpose:** Centralized configuration management for API credentials, SMTP settings, and system parameters.

**Interface:**
```python
class Config:
    def __init__(self, config_file: Optional[str] = None)
    def get_slack_token(self) -> str
    def get_gmail_credentials_path(self) -> str
    def get_smtp_settings(self) -> dict
    def get_recipient_email(self) -> str
    def get_schedule_time(self) -> str
    def validate(self) -> bool
```

**Configuration Sources:**
- Environment variables (primary)
- Configuration file (`.env` or `config.json`)
- Default values (where appropriate)

**Key Settings:**
- `SLACK_BOT_TOKEN`: Slack API authentication token
- `GMAIL_CREDENTIALS_PATH`: Path to Gmail OAuth2 credentials JSON
- `GMAIL_TOKEN_PATH`: Path to store Gmail OAuth2 token
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Email sending configuration
- `RECIPIENT_EMAIL`: Destination email for the digest
- `SCHEDULE_TIME`: Daily execution time (default: "20:00")

### 2. Message Collector Interface

All message collectors implement a common interface to ensure consistency:

```python
class MessageCollector(ABC):
    @abstractmethod
    def collect(self) -> List[Message]
    
    @abstractmethod
    def get_source_name(self) -> str
```

**Message Data Model:**
```python
@dataclass
class Message:
    source: str          # "slack", "gmail", "whatsapp"
    sender: str          # Sender name or email
    sender_detail: str   # Channel name, email address, or phone number
    content: str         # Message content or email subject
    timestamp: datetime  # When the message was sent
    message_type: str    # "channel", "direct", "email", "chat"
```

### 3. Slack Collector (`collectors/slack_collector.py`)

**Purpose:** Retrieves unread messages from Slack using the Slack Web API.

**Implementation Details:**
- Uses `slack_sdk` Python library
- Authenticates with bot token
- Retrieves conversations list and unread messages from each
- Handles both channel messages and direct messages
- Extracts message text, sender username, channel name, and timestamp

**API Methods Used:**
- `conversations.list`: Get all accessible channels
- `conversations.history`: Retrieve messages from channels
- `users.info`: Get user display names

**Error Handling:**
- Network errors: Log and return empty collection
- Authentication errors: Log detailed error and return empty collection
- Rate limiting: Implement exponential backoff

### 4. Gmail Collector (`collectors/gmail_collector.py`)

**Purpose:** Retrieves unread emails from Gmail using the Gmail API.

**Implementation Details:**
- Uses `google-auth` and `google-api-python-client` libraries
- Implements OAuth2 authentication flow
- Queries for unread messages in inbox
- Extracts subject, sender name, sender email, and date
- Marks messages as read (optional configuration)

**API Methods Used:**
- `users.messages.list`: Query unread messages
- `users.messages.get`: Retrieve full message details
- `users.messages.modify`: Mark as read (optional)

**Authentication Flow:**
1. Check for existing token file
2. If token exists and valid, use it
3. If token expired, refresh it
4. If no token, initiate OAuth2 flow (requires user interaction on first run)

**Error Handling:**
- Authentication errors: Provide clear instructions for credential setup
- Network errors: Log and return empty collection
- API quota exceeded: Log warning and return partial results

### 5. WhatsApp Collector (`collectors/whatsapp_collector.py`)

**Purpose:** Placeholder implementation for WhatsApp message collection.

**Implementation Details:**
- Returns mock data in the standardized Message format
- Logs a message indicating placeholder status
- Designed for future integration with Twilio API or WhatsApp Business API

**Mock Data Structure:**
```python
[
    Message(
        source="whatsapp",
        sender="Contact Name",
        sender_detail="+1234567890",
        content="Message preview...",
        timestamp=datetime.now(),
        message_type="chat"
    )
]
```

**Future Integration Notes:**
- Twilio API for WhatsApp Business
- WhatsApp Cloud API as alternative
- Webhook-based message collection

### 6. Digest Generator (`digest_generator.py`)

**Purpose:** Formats collected messages into readable plain text and HTML digests.

**Interface:**
```python
class DigestGenerator:
    def generate(self, messages: List[Message]) -> Tuple[str, str]
    def _generate_plain_text(self, grouped_messages: Dict) -> str
    def _generate_html(self, grouped_messages: Dict) -> str
    def _group_by_source(self, messages: List[Message]) -> Dict
    def _sort_by_timestamp(self, messages: List[Message]) -> List[Message]
```

**Plain Text Format:**
```
Daily Digest - December 5, 2025
Total Notifications: 15

=== SLACK (8 messages) ===
• #general - John Doe (2:30 PM)
  "Meeting rescheduled to 3 PM"

• Direct Message - Jane Smith (3:45 PM)
  "Can you review the PR?"

=== GMAIL (5 emails) ===
• From: client@example.com (1:15 PM)
  Subject: "Project Update Required"

=== WHATSAPP (2 messages) ===
• Contact Name (4:20 PM)
  "Message preview..."
```

**HTML Format:**
- Professional styling with CSS
- Responsive design for mobile viewing
- Color-coded sections by source
- Clickable links where applicable
- Summary header with total counts

### 7. Email Sender (`email_sender.py`)

**Purpose:** Sends the formatted digest via SMTP.

**Interface:**
```python
class EmailSender:
    def __init__(self, config: Config)
    def send_digest(self, plain_text: str, html: str, message_count: int) -> bool
    def send_error_notification(self, error_message: str) -> bool
```

**Implementation Details:**
- Uses Python's `smtplib` and `email.mime` modules
- Creates multipart email with both plain text and HTML
- Subject line format: "Daily Digest - [Date] - [Count] notifications"
- Supports TLS/SSL encryption
- Implements connection retry logic

**SMTP Configuration:**
- Supports common providers (Gmail, Outlook, custom SMTP)
- Configurable port (587 for TLS, 465 for SSL)
- Authentication with username/password

### 8. Orchestrator (`main.py`)

**Purpose:** Coordinates the entire workflow and handles high-level error management.

**Workflow:**
```python
def main():
    1. Load configuration
    2. Initialize logger
    3. Initialize all collectors
    4. Collect messages from all sources (with error handling per source)
    5. Generate digest
    6. Send email
    7. Log execution summary
    8. Handle critical errors with notification email
```

**Error Handling Strategy:**
- Collector failures: Log error, continue with other collectors
- Digest generation failure: Log error, send error notification email
- Email sending failure: Log error, raise exception
- Critical errors: Send error notification to user

**Logging:**
- Log level: INFO for normal operations, ERROR for failures
- Log format: Timestamp, level, component, message
- Log destination: Console and file (`logs/digest_maker.log`)

## Data Models

### Message

```python
@dataclass
class Message:
    source: str          # Platform identifier
    sender: str          # Display name of sender
    sender_detail: str   # Additional identifier (email, channel, phone)
    content: str         # Message text or subject
    timestamp: datetime  # Message timestamp
    message_type: str    # Type classification
    
    def to_dict(self) -> dict
    def from_dict(data: dict) -> Message
```

### DigestData

```python
@dataclass
class DigestData:
    messages_by_source: Dict[str, List[Message]]
    total_count: int
    generation_time: datetime
    
    def get_source_count(self, source: str) -> int
    def get_all_messages_sorted(self) -> List[Message]
```

### Configuration

```python
@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    
@dataclass
class AppConfig:
    slack_token: Optional[str]
    gmail_credentials_path: Optional[str]
    gmail_token_path: str
    smtp: SMTPConfig
    recipient_email: str
    schedule_time: str
    log_level: str
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated to eliminate redundancy:

- Message extraction properties (1.3, 2.3, 3.5) all verify that required fields are present in collected messages - these can be combined into a single property about the Message interface
- Empty collection handling (1.5, 2.5, 4.5) are edge cases that will be naturally covered by property tests with empty inputs
- Grouping and sorting (4.1, 4.2) can be tested together as they're part of the same digest generation process
- Format properties (5.1, 5.3, 5.4, 5.5) all verify digest content structure and can be consolidated

### Core Properties

**Property 1: Message collection completeness**
*For any* set of unread messages available through an API, the collector should retrieve all accessible messages without omission.
**Validates: Requirements 1.2, 2.2**

**Property 2: Message data integrity**
*For any* collected message, the Message object should contain all required fields (source, sender, sender_detail, content, timestamp, message_type) with non-null values.
**Validates: Requirements 1.3, 2.3, 3.2, 3.5**

**Property 3: Interface compatibility**
*For any* message collector implementation, the returned collection should conform to the MessageCollector interface and return a list of valid Message objects.
**Validates: Requirements 8.4, 8.5**

**Property 4: Message grouping correctness**
*For any* collection of messages from multiple sources, grouping by source should result in each message appearing in exactly one group corresponding to its source field.
**Validates: Requirements 4.1**

**Property 5: Timestamp ordering**
*For any* group of messages, sorting by timestamp in descending order should result in messages ordered from most recent to oldest.
**Validates: Requirements 4.2**

**Property 6: Dual format generation**
*For any* collection of messages, the digest generator should produce both a plain text string and an HTML string, both non-empty when messages exist.
**Validates: Requirements 4.3**

**Property 7: Digest content completeness**
*For any* collection of messages, the generated digest (both plain text and HTML) should include the message count per source, sender information, and content preview for each message.
**Validates: Requirements 4.4, 5.5**

**Property 8: Timestamp formatting consistency**
*For any* message timestamp, the formatted timestamp in the digest should include both date and time components in a human-readable format.
**Validates: Requirements 5.3**

**Property 9: Sender information structure**
*For any* message in the digest, the sender display should include the sender name and sender_detail in a consistent format.
**Validates: Requirements 5.4**

**Property 10: Plain text structure**
*For any* generated plain text digest, it should contain section headers for each source with messages, and use consistent formatting (bullets, spacing).
**Validates: Requirements 5.1**

**Property 11: Email multipart structure**
*For any* digest email, the email message should contain both a plain text part and an HTML part with the respective digest content.
**Validates: Requirements 6.2**

**Property 12: Subject line format**
*For any* digest email, the subject line should include the current date and the total count of notifications.
**Validates: Requirements 6.3**

**Property 13: Error resilience**
*For any* collector that fails during execution, the orchestrator should continue executing remaining collectors and still generate a digest with available messages.
**Validates: Requirements 7.4**

**Property 14: Standardized return format**
*For any* collector execution (success or failure), the collector should return a list of Message objects (empty list on failure) without raising exceptions.
**Validates: Requirements 8.5**

**Property 15: Credential security in logs**
*For any* log output generated by the system, the log content should not contain sensitive credentials (tokens, passwords, API keys) in plain text.
**Validates: Requirements 9.4**

**Property 16: API response validation**
*For any* API response received, the system should validate the response structure before processing and handle malformed responses without crashing.
**Validates: Requirements 11.3**

## Error Handling

### Error Categories

1. **Authentication Errors**
   - Invalid credentials
   - Expired tokens
   - Missing configuration
   - **Handling:** Log detailed error, return empty collection, continue workflow

2. **Network Errors**
   - Connection timeout
   - DNS resolution failure
   - API unavailable
   - **Handling:** Implement retry with exponential backoff (3 attempts), log error, return empty collection

3. **API Errors**
   - Rate limiting
   - Invalid request
   - Quota exceeded
   - **Handling:** Log error with API response details, return partial results or empty collection

4. **Data Processing Errors**
   - Malformed API response
   - Missing required fields
   - Invalid data types
   - **Handling:** Log error with data context, skip invalid items, continue processing valid items

5. **Email Sending Errors**
   - SMTP authentication failure
   - Connection refused
   - Invalid recipient
   - **Handling:** Log detailed error, send error notification to fallback email if configured, raise exception

6. **Critical Errors**
   - Configuration file missing
   - All collectors failed
   - Digest generation failed
   - **Handling:** Log critical error, attempt to send error notification email, exit with error code

### Error Logging Format

```python
{
    "timestamp": "2025-12-05T20:00:15Z",
    "level": "ERROR",
    "component": "SlackCollector",
    "error_type": "AuthenticationError",
    "message": "Failed to authenticate with Slack API",
    "details": {
        "error_code": "invalid_auth",
        "api_response": "token_revoked"
    },
    "context": {
        "execution_id": "uuid",
        "retry_attempt": 1
    }
}
```

### Retry Strategy

- **Network errors:** 3 attempts with exponential backoff (1s, 2s, 4s)
- **Rate limiting:** Respect Retry-After header, max 2 retries
- **Authentication errors:** No retry (requires user intervention)
- **Transient errors:** 2 attempts with 2s delay

## Testing Strategy

The Daily Digest Maker will employ a comprehensive testing approach combining unit tests and property-based tests to ensure correctness and reliability.

### Property-Based Testing

**Framework:** We will use `hypothesis` for Python, which is the standard property-based testing library.

**Configuration:** Each property-based test will run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Test Tagging:** Each property-based test will include a comment explicitly referencing the correctness property from this design document using the format:
```python
# Feature: daily-digest-maker, Property 1: Message collection completeness
```

**Property Test Coverage:**

1. **Message Data Integrity (Property 2)**
   - Generate random Message objects with various field values
   - Verify all required fields are present and non-null
   - Test with edge cases: empty strings, special characters, extreme timestamps

2. **Interface Compatibility (Property 3)**
   - Generate random message collections
   - Verify all collectors return List[Message] type
   - Test that Message objects can be serialized/deserialized

3. **Message Grouping (Property 4)**
   - Generate random collections with mixed sources
   - Verify each message appears in exactly one group
   - Verify group keys match message source values
   - Test with empty collections and single-source collections

4. **Timestamp Ordering (Property 5)**
   - Generate random message collections with random timestamps
   - Verify sorted order is descending
   - Test with duplicate timestamps
   - Test with messages spanning multiple days

5. **Dual Format Generation (Property 6)**
   - Generate random message collections
   - Verify both plain text and HTML are non-empty when messages exist
   - Verify both are empty strings when no messages exist

6. **Digest Content Completeness (Property 7)**
   - Generate random message collections
   - Verify all message counts, senders, and content appear in output
   - Use string matching to verify presence of required elements

7. **Timestamp Formatting (Property 8)**
   - Generate random timestamps
   - Verify formatted output contains date and time
   - Verify format is consistent across all timestamps

8. **Sender Information Structure (Property 9)**
   - Generate random messages with various sender formats
   - Verify sender name and detail both appear in digest
   - Verify consistent formatting across all messages

9. **Plain Text Structure (Property 10)**
   - Generate random message collections
   - Verify section headers exist for each source
   - Verify bullet points or consistent formatting is used

10. **Email Multipart Structure (Property 11)**
    - Generate random digest content
    - Verify email has both text/plain and text/html parts
    - Verify content matches generated digests

11. **Subject Line Format (Property 12)**
    - Generate random message counts and dates
    - Verify subject contains date string
    - Verify subject contains count number

12. **Standardized Return Format (Property 14)**
    - Simulate various collector states (success, failure, partial)
    - Verify return type is always List[Message]
    - Verify no exceptions are raised

13. **Credential Security (Property 15)**
    - Generate log messages with various content
    - Verify no credential patterns appear in logs
    - Test with actual credential formats (tokens, passwords)

14. **API Response Validation (Property 16)**
    - Generate malformed API responses
    - Verify system handles them gracefully
    - Verify no crashes or unhandled exceptions

### Unit Testing

Unit tests will cover specific examples, integration points, and error conditions:

1. **Configuration Loading**
   - Test loading from environment variables
   - Test loading from config file
   - Test missing required configuration
   - Test invalid configuration values

2. **Authentication Flows**
   - Test successful Slack authentication
   - Test successful Gmail OAuth2 flow
   - Test authentication failure handling
   - Test token refresh for Gmail

3. **API Integration**
   - Test Slack API message retrieval with mock responses
   - Test Gmail API message retrieval with mock responses
   - Test API error responses
   - Test rate limiting handling

4. **Digest Generation**
   - Test digest with messages from all sources
   - Test digest with messages from single source
   - Test digest with no messages
   - Test HTML escaping of special characters

5. **Email Sending**
   - Test SMTP connection and authentication
   - Test email composition with multipart content
   - Test email sending failure handling

6. **Orchestrator Integration**
   - Test complete workflow with all components
   - Test workflow with collector failures
   - Test workflow with email sending failure
   - Test error notification sending

7. **Error Handling**
   - Test retry logic with transient failures
   - Test error logging format
   - Test graceful degradation when collectors fail

### Test Organization

```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_slack_collector.py
│   ├── test_gmail_collector.py
│   ├── test_whatsapp_collector.py
│   ├── test_digest_generator.py
│   ├── test_email_sender.py
│   └── test_orchestrator.py
├── property/
│   ├── test_message_properties.py
│   ├── test_digest_properties.py
│   ├── test_email_properties.py
│   └── test_security_properties.py
└── integration/
    └── test_end_to_end.py
```

### Testing Best Practices

- Mock external API calls to avoid dependencies on external services
- Use test fixtures for common test data
- Implement custom Hypothesis strategies for Message generation
- Test both success and failure paths
- Verify logging output in tests
- Use parameterized tests for similar test cases with different inputs
- Maintain test coverage above 80% for core components

## Security Considerations

1. **Credential Storage**
   - Never hardcode credentials in source code
   - Use environment variables or secure configuration files
   - Add credential files to .gitignore
   - Use OAuth2 for Gmail (more secure than app passwords)

2. **Credential Transmission**
   - Always use TLS/SSL for SMTP connections
   - Use HTTPS for all API requests
   - Never log credentials in plain text

3. **Token Management**
   - Store Gmail OAuth2 tokens securely
   - Implement token refresh logic
   - Handle token expiration gracefully

4. **Email Content**
   - Sanitize HTML content to prevent XSS
   - Escape special characters in plain text
   - Validate email addresses before sending

5. **Error Messages**
   - Don't expose sensitive information in error messages
   - Sanitize error logs to remove credentials
   - Use generic error messages for authentication failures

## Performance Considerations

1. **Parallel Collection**
   - Collectors can run in parallel using threading or asyncio
   - Reduces total execution time when multiple sources are configured
   - Each collector is independent and doesn't block others

2. **API Rate Limiting**
   - Respect API rate limits for each platform
   - Implement exponential backoff for rate limit errors
   - Cache API responses when appropriate

3. **Message Limits**
   - Limit number of messages retrieved per source (configurable)
   - Implement pagination for large message volumes
   - Truncate very long message content in digest

4. **Email Size**
   - Monitor digest size to stay within email size limits
   - Compress or truncate content if necessary
   - Consider attachment for very large digests

## Deployment Considerations

1. **Environment Setup**
   - Python 3.8+ required
   - Virtual environment recommended
   - Dependencies installed via pip

2. **Scheduler Configuration**
   - Cron job for Linux/Mac
   - Task Scheduler for Windows
   - Cloud scheduler for cloud deployments (AWS EventBridge, Google Cloud Scheduler)

3. **Logging**
   - Log rotation to prevent disk space issues
   - Centralized logging for cloud deployments
   - Log level configuration via environment variable

4. **Monitoring**
   - Track execution success/failure rates
   - Monitor API quota usage
   - Alert on consecutive failures

5. **Configuration Management**
   - Use .env files for local development
   - Use secrets management for production (AWS Secrets Manager, etc.)
   - Document all required configuration variables

## Future Enhancements

1. **Additional Sources**
   - Microsoft Teams integration
   - Discord integration
   - Twitter/X mentions

2. **Advanced Features**
   - AI-powered summarization of message content
   - Priority detection for urgent messages
   - Custom filtering rules
   - Multiple digest schedules (morning and evening)

3. **User Interface**
   - Web dashboard for configuration
   - Mobile app for digest viewing
   - Interactive digest with action buttons

4. **Analytics**
   - Message volume trends
   - Response time tracking
   - Source usage statistics

## Technology Stack

- **Language:** Python 3.8+
- **Slack Integration:** slack-sdk
- **Gmail Integration:** google-auth, google-auth-oauthlib, google-api-python-client
- **Email:** smtplib (standard library), email.mime (standard library)
- **Configuration:** python-dotenv
- **Logging:** logging (standard library)
- **Testing:** pytest, hypothesis
- **Scheduling:** cron (Linux/Mac), Task Scheduler (Windows), or APScheduler (Python-based)
- **Date/Time:** datetime (standard library), pytz for timezone handling

## Project Structure

```
daily-digest-maker/
├── .env.example              # Example configuration file
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup file
├── main.py                  # Orchestrator entry point
├── config.py                # Configuration management
├── models.py                # Data models (Message, Config, etc.)
├── collectors/
│   ├── __init__.py
│   ├── base.py             # MessageCollector interface
│   ├── slack_collector.py  # Slack integration
│   ├── gmail_collector.py  # Gmail integration
│   └── whatsapp_collector.py  # WhatsApp placeholder
├── digest_generator.py      # Digest formatting
├── email_sender.py          # Email delivery
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   └── retry.py            # Retry logic utilities
├── logs/                    # Log files directory
├── credentials/             # API credentials (gitignored)
│   └── gmail_credentials.json
└── tests/                   # Test suite
    ├── unit/
    ├── property/
    └── integration/
```
