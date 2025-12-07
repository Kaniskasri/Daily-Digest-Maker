"""Logging configuration with credential sanitization."""
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from typing import Any


class CredentialSanitizer(logging.Filter):
    """Filter to sanitize credentials from log messages."""
    
    # Patterns for common credential formats
    PATTERNS = [
        (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(bearer\s+)([^\s]+)', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(xox[baprs]-[^\s]+)', re.IGNORECASE), r'***REDACTED***'),  # Slack tokens
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize the log record message."""
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        
        # Sanitize args if present
        if record.args:
            sanitized_args = []
            for arg in record.args if isinstance(record.args, tuple) else [record.args]:
                if isinstance(arg, str):
                    for pattern, replacement in self.PATTERNS:
                        arg = pattern.sub(replacement, arg)
                sanitized_args.append(arg)
            record.args = tuple(sanitized_args) if isinstance(record.args, tuple) else sanitized_args[0]
        
        return True


def setup_logger(name: str, log_level: str = "INFO", log_file: str = "logs/digest_maker.log") -> logging.Logger:
    """Set up logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CredentialSanitizer())
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    file_handler.addFilter(CredentialSanitizer())
    logger.addHandler(file_handler)
    
    return logger
