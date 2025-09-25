"""
Netflix VerifyBot - Automated Netflix Email Verification

A Python application that monitors an email inbox for Netflix verification emails
and automatically processes them by clicking verification links and extracting
verification codes.

This package provides a modular architecture for:
- Email handling and IMAP management
- Web scraping for Netflix verification links
- Telegram notifications
- Configuration management
- Comprehensive logging

Author: Refactored for better structure and maintainability
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Netflix VerifyBot Team"
__description__ = "Automated Netflix Email Verification Bot"

# Import main components for easy access
from .config import Config, load_config, validate_config, ConfigError
from .notifications import NotificationHandler, NotificationError
from .email_handler import EmailHandler, EmailConnectionError, EmailProcessingError
from .web_scraper import WebScraper, WebScrapingManager, WebScrapingError
from .app import NetflixVerifyBot

__all__ = [
    "Config",
    "load_config", 
    "validate_config",
    "ConfigError",
    "NotificationHandler",
    "NotificationError",
    "EmailHandler",
    "EmailConnectionError",
    "EmailProcessingError",
    "WebScraper",
    "WebScrapingManager", 
    "WebScrapingError",
    "NetflixVerifyBot"
]
