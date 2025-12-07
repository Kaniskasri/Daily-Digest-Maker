"""Simple SMTP test script to verify email credentials."""
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get credentials
smtp_host = os.getenv('SMTP_HOST')
smtp_port = int(os.getenv('SMTP_PORT'))
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')
recipient = os.getenv('RECIPIENT_EMAIL')

print("=" * 60)
print("SMTP Configuration Test")
print("=" * 60)
print(f"Host: {smtp_host}")
print(f"Port: {smtp_port}")
print(f"Username: {smtp_username}")
print(f"Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")
print(f"Password length: {len(smtp_password) if smtp_password else 0} characters")
print(f"Recipient: {recipient}")
print("=" * 60)

# Check for common issues
issues = []
if not smtp_password:
    issues.append("❌ Password is empty!")
elif ' ' in smtp_password:
    issues.append("❌ Password contains spaces! Remove all spaces.")
elif len(smtp_password) != 16:
    issues.append(f"⚠️  Password length is {len(smtp_password)}, should be 16 characters")

if issues:
    print("\nIssues found:")
    for issue in issues:
        print(f"  {issue}")
    print("\nPlease fix these issues in your .env file")
    exit(1)

print("\n✅ Configuration looks good!")
print("\nTesting SMTP connection...")

try:
    # Connect to SMTP server
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    print("✅ Connected to SMTP server")
    
    # Try to login
    server.login(smtp_username, smtp_password)
    print("✅ Login successful!")
    
    # Send test email
    msg = MIMEText("This is a test email from Daily Digest Maker")
    msg['Subject'] = "SMTP Test - Success!"
    msg['From'] = smtp_username
    msg['To'] = recipient
    
    server.send_message(msg)
    print("✅ Test email sent successfully!")
    
    server.quit()
    print("\n" + "=" * 60)
    print("SUCCESS! Your SMTP configuration is working!")
    print("=" * 60)
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\nPossible solutions:")
    print("1. Generate a NEW app password at: https://myaccount.google.com/apppasswords")
    print("2. Make sure 2-Factor Authentication is enabled")
    print("3. Remove ALL spaces from the app password")
    print("4. Make sure you're using the app password, not your regular password")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
