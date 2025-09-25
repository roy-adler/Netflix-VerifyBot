"""
Configuration management for Netflix VerifyBot.

This module handles all configuration loading, validation, and provides
a centralized configuration object for the entire application.
"""

import os
import ssl
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback if dotenv is not available
    def load_dotenv(filename: str = ".env") -> None:
        """Fallback function when dotenv is not available."""
        pass


@dataclass
class EmailConfig:
    """Email configuration settings."""
    email: str
    password: str
    imap_server: str
    imap_port: int
    ssl_context: ssl.SSLContext


@dataclass
class TelegramConfig:
    """Telegram notification configuration settings."""
    api_key: Optional[str]
    api_url: Optional[str]
    channel_name: Optional[str]
    channel_secret: Optional[str]
    enabled: bool


@dataclass
class AppConfig:
    """Main application configuration settings."""
    check_interval: int
    minutes_to_wait: int
    max_retry_attempts: int
    log_path: str
    gelesen_folder: str


@dataclass
class Config:
    """Complete application configuration."""
    email: EmailConfig
    telegram: TelegramConfig
    app: AppConfig


class ConfigError(Exception):
    """Raised when there's an error in configuration loading or validation."""
    pass


def load_config(config_file: str = "config.env") -> Config:
    """
    Load and validate configuration from environment variables.
    
    Args:
        config_file: Path to the configuration file to load.
        
    Returns:
        Config: Validated configuration object.
        
    Raises:
        ConfigError: If required configuration is missing or invalid.
    """
    # Load environment variables
    load_dotenv(config_file)
    
    # Load email configuration
    email_config = _load_email_config()
    
    # Load telegram configuration
    telegram_config = _load_telegram_config()
    
    # Load app configuration
    app_config = _load_app_config()
    
    return Config(
        email=email_config,
        telegram=telegram_config,
        app=app_config
    )


def _load_email_config() -> EmailConfig:
    """Load and validate email configuration."""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    imap_server = os.getenv("IMAP_SERVER")
    imap_port_str = os.getenv("IMAP_PORT", "993")
    
    if not all([email, password, imap_server]):
        raise ConfigError("Missing required email configuration: EMAIL, PASSWORD, or IMAP_SERVER")
    
    try:
        imap_port = int(imap_port_str)
    except ValueError:
        raise ConfigError(f"Invalid IMAP_PORT: {imap_port_str}. Must be a valid integer.")
    
    ssl_context = ssl.create_default_context()
    
    return EmailConfig(
        email=email,
        password=password,
        imap_server=imap_server,
        imap_port=imap_port,
        ssl_context=ssl_context
    )


def _load_telegram_config() -> TelegramConfig:
    """Load and validate telegram configuration."""
    api_key = os.getenv("TELEGRAM_API_KEY")
    api_url = os.getenv("TELEGRAM_API_URL")
    channel_name = os.getenv("TELEGRAM_CHANNEL_NAME")
    channel_secret = os.getenv("TELEGRAM_CHANNEL_SECRET")
    
    # Telegram is enabled only if all required fields are present
    enabled = bool(api_key and api_url and channel_name and channel_secret)
    
    return TelegramConfig(
        api_key=api_key,
        api_url=api_url,
        channel_name=channel_name,
        channel_secret=channel_secret,
        enabled=enabled
    )


def _load_app_config() -> AppConfig:
    """Load and validate application configuration."""
    check_interval = int(os.getenv("CHECK_INTERVAL", "3"))
    minutes_to_wait = int(os.getenv("MINUTES_TO_WAIT", "900"))
    max_retry_attempts = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    log_path = os.getenv("LOG_PATH", "netflix-validator.log")
    gelesen_folder = os.getenv("GELESEN_FOLDER", "Gelesen")
    
    return AppConfig(
        check_interval=check_interval,
        minutes_to_wait=minutes_to_wait,
        max_retry_attempts=max_retry_attempts,
        log_path=log_path,
        gelesen_folder=gelesen_folder
    )


def validate_config(config: Config) -> None:
    """
    Validate the loaded configuration.
    
    Args:
        config: Configuration object to validate.
        
    Raises:
        ConfigError: If configuration is invalid.
    """
    # Validate email configuration
    if not config.email.email or "@" not in config.email.email:
        raise ConfigError("Invalid email address")
    
    if not config.email.password:
        raise ConfigError("Email password cannot be empty")
    
    if not config.email.imap_server:
        raise ConfigError("IMAP server cannot be empty")
    
    if not (1 <= config.email.imap_port <= 65535):
        raise ConfigError(f"Invalid IMAP port: {config.email.imap_port}")
    
    # Validate app configuration
    if config.app.check_interval <= 0:
        raise ConfigError(f"Invalid check interval: {config.app.check_interval}")
    
    if config.app.minutes_to_wait <= 0:
        raise ConfigError(f"Invalid minutes to wait: {config.app.minutes_to_wait}")
    
    if config.app.max_retry_attempts <= 0:
        raise ConfigError(f"Invalid max retry attempts: {config.app.max_retry_attempts}")
    
    # Validate telegram configuration if enabled
    if config.telegram.enabled:
        if not config.telegram.api_url.startswith(('http://', 'https://')):
            raise ConfigError(f"Invalid Telegram API URL: {config.telegram.api_url}")
        
        if len(config.telegram.api_key) < 10:
            raise ConfigError("Telegram API key appears to be invalid (too short)")
