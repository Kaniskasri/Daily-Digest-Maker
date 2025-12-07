# Daily Digest Maker

An automated system that consolidates unread notifications from multiple communication platforms (Slack, Gmail, and WhatsApp) into a single, beautifully formatted email digest delivered daily at your preferred time.

## Features

- 📧 **Multi-Platform Integration**: Collects messages from Slack, Gmail, and WhatsApp
- 🎨 **Beautiful Formatting**: Professional HTML email with responsive design
- ⏰ **Automated Scheduling**: Set it and forget it with cron or Task Scheduler
- 🔒 **Secure Configuration**: Environment-based credential management
- 📊 **Smart Organization**: Messages grouped by source and sorted by time
- 🛡️ **Robust Error Handling**: Continues working even if one source fails
- 📝 **Comprehensive Logging**: Detailed logs with credential sanitization

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials (see Configuration section below)

### Configuration

#### Required Settings

Edit your `.env` file with these required settings:

```env
# SMTP Configuration (required for sending emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com
```

#### Optional Platform Integrations

**Slack Integration:**

1. Create a Slack App at https://api.slack.com/apps
2. Add the following OAuth scopes:
   - `channels:history`
   - `channels:read`
   - `im:history`
   - `im:read`
   - `users:read`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token to your `.env`:
   ```env
   SLACK_BOT_TOKEN=xoxb-your-token-here
   ```

**Gmail Integration:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials JSON file
6. Save it as `credentials/gmail_credentials.json`
7. Update your `.env`:
   ```env
   GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json
   GMAIL_TOKEN_PATH=credentials/gmail_token.json
   ```

**WhatsApp Integration:**

Currently uses placeholder data. Future integration with Twilio API or WhatsApp Business API planned.

#### SMTP Provider Setup

**Gmail:**
- Use App Passwords (not your regular password)
- Enable 2-factor authentication on your Google account
- Generate an App Password at https://myaccount.google.com/apppasswords
- Use `smtp.gmail.com` with port `587`

**Outlook/Hotmail:**
- Use your regular password
- Use `smtp-mail.outlook.com` with port `587`

**Other Providers:**
- Check your email provider's SMTP settings
- Update `SMTP_HOST` and `SMTP_PORT` accordingly

### Running the Digest

**Manual Execution:**
```bash
python main.py
```

**Scheduled Execution:**

**On Linux/macOS (using cron):**

1. Open crontab editor:
   ```bash
   crontab -e
   ```

2. Add this line to run daily at 8 PM:
   ```cron
   0 20 * * * cd /path/to/daily-digest-maker && /path/to/venv/bin/python main.py
   ```

3. Example with full paths:
   ```cron
   0 20 * * * cd /home/user/daily-digest-maker && /home/user/daily-digest-maker/venv/bin/python /home/user/daily-digest-maker/main.py
   ```

**On Windows (using Task Scheduler):**

1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name: "Daily Digest Maker"
4. Trigger: Daily at 8:00 PM
5. Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\main.py`
   - Start in: `C:\path\to\daily-digest-maker`

## Project Structure

```
daily-digest-maker/
├── main.py                  # Main orchestrator
├── config.py                # Configuration management
├── models.py                # Data models
├── digest_generator.py      # Digest formatting
├── email_sender.py          # Email delivery
├── collectors/              # Message collectors
│   ├── __init__.py
│   ├── base.py             # Base interface
│   ├── slack_collector.py  # Slack integration
│   ├── gmail_collector.py  # Gmail integration
│   └── whatsapp_collector.py  # WhatsApp placeholder
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── logger.py           # Logging with sanitization
│   └── retry.py            # Retry logic
├── tests/                   # Test suite
├── logs/                    # Log files (auto-created)
├── credentials/             # API credentials (gitignored)
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (gitignored)
├── .env.example            # Configuration template
└── README.md               # This file
```

## Troubleshooting

### Gmail OAuth Issues

**Problem:** "The OAuth client was not found"
- Ensure `gmail_credentials.json` is in the correct location
- Verify the file contains valid OAuth 2.0 credentials

**Problem:** First run requires browser authentication
- This is normal! Gmail requires one-time authorization
- A browser window will open automatically
- After authorization, a token file is saved for future use

### SMTP Authentication Errors

**Problem:** "Username and Password not accepted"
- For Gmail: Use an App Password, not your regular password
- Ensure 2-factor authentication is enabled
- Check that `SMTP_USERNAME` matches the email you're sending from

### Slack API Errors

**Problem:** "invalid_auth" error
- Verify your bot token starts with `xoxb-`
- Ensure the app is installed to your workspace
- Check that required OAuth scopes are added

### No Messages Collected

**Problem:** Digest shows 0 messages
- This is normal if you have no unread messages
- Check that the collectors are configured correctly
- Review logs in `logs/digest_maker.log` for errors

## How Kiro Accelerated Development

This project was developed using Kiro, an AI-powered development assistant, which significantly accelerated the development process:

- **Rapid Prototyping**: Kiro helped scaffold the entire project structure in minutes
- **Best Practices**: Implemented proper error handling, logging, and retry logic from the start
- **Comprehensive Testing**: Generated property-based and unit tests for robust validation
- **Documentation**: Created detailed README and inline documentation automatically
- **Code Quality**: Ensured consistent coding standards and patterns throughout

What would typically take days of development was completed in hours, with production-ready code that follows industry best practices.

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Future Enhancements

- WhatsApp integration via Twilio API
- Microsoft Teams support
- Discord integration
- AI-powered message summarization
- Priority detection for urgent messages
- Web dashboard for configuration
- Multiple digest schedules
- Custom filtering rules

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review logs in `logs/digest_maker.log`
3. Open an issue on GitHub

---

Made with ❤️ using Kiro
