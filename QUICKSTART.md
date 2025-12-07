# Quick Start Guide

Get your Daily Digest Maker up and running in 5 minutes!

## 1. Initial Setup (One-time)

```bash
# Run the setup script
python setup_project.py

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure Your Credentials

Edit the `.env` file with your credentials:

### Minimum Required (for testing):
```env
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com
```

### Optional Platform Integrations:
```env
# Slack (optional)
SLACK_BOT_TOKEN=xoxb-your-token

# Gmail (optional)
GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json
```

## 3. Test Run

```bash
# Run manually to test
python main.py
```

You should receive an email digest within a few seconds!

## 4. Schedule Daily Execution

### On Linux/macOS:
```bash
# Edit crontab
crontab -e

# Add this line (runs at 8 PM daily)
0 20 * * * cd /path/to/daily-digest-maker && /path/to/python main.py
```

### On Windows:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 8:00 PM
4. Set action: Start program `python.exe` with argument `main.py`

## Troubleshooting

### "Configuration validation failed"
- Make sure you've set `SMTP_USERNAME`, `SMTP_PASSWORD`, and `RECIPIENT_EMAIL` in `.env`

### "SMTP authentication failed"
- For Gmail: Use an App Password, not your regular password
- Enable 2-factor authentication first
- Generate App Password at: https://myaccount.google.com/apppasswords

### "No module named 'slack_sdk'"
- Run: `pip install -r requirements.txt`

### Gmail OAuth requires browser
- This is normal on first run
- A browser window will open for authorization
- After authorization, a token is saved for future use

## Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test types
pytest tests/unit/          # Unit tests only
pytest tests/property/      # Property-based tests only
```

## What's Next?

- Check `logs/digest_maker.log` for execution details
- Customize the schedule time in `.env` (SCHEDULE_TIME=09:00)
- Add more platform integrations (Slack, Gmail)
- Review the full README.md for detailed documentation

## Getting Help

- Check the main README.md for detailed setup instructions
- Review logs in `logs/digest_maker.log`
- Ensure all credentials are correctly configured in `.env`

---

**Pro Tip**: Run `python main.py` manually first to test your configuration before setting up the scheduler!
