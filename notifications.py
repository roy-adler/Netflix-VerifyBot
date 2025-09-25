"""
Notification and logging module for Netflix VerifyBot.

This module handles all logging operations and Telegram notifications.
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime

from config import TelegramConfig


class NotificationError(Exception):
    """Raised when there's an error with notifications."""
    pass


class NotificationHandler:
    """Handles all notification and logging operations."""
    
    def __init__(self, telegram_config: TelegramConfig, log_path: str):
        """
        Initialize the notification handler.
        
        Args:
            telegram_config: Telegram configuration settings.
            log_path: Path to the log file.
        """
        self.telegram_config = telegram_config
        self.log_path = log_path
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging configuration.
        
        Returns:
            logging.Logger: Configured logger instance.
        """
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_path),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        return logging.getLogger(__name__)
    
    def log_info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: Message to log.
        """
        self.logger.info(message)
        self._broadcast_to_telegram(message)
    
    def log_warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Message to log.
        """
        self.logger.warning(message)
        self._broadcast_to_telegram(message)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log.
        """
        self.logger.error(message)
        self._broadcast_to_telegram(message)
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Message to log.
        """
        self.logger.debug(message)
        # Debug messages are not broadcast to Telegram
    
    def log_and_broadcast(self, message: str, level: str = "INFO") -> None:
        """
        Log a message and broadcast to Telegram.
        
        Args:
            message: Message to log and broadcast.
            level: Log level (INFO, WARNING, ERROR, DEBUG).
        """
        if level == "INFO":
            self.log_info(message)
        elif level == "WARNING":
            self.log_warning(message)
        elif level == "ERROR":
            self.log_error(message)
        elif level == "DEBUG":
            self.log_debug(message)
        else:
            # Fallback to print if logger not initialized
            print(f"[{level}] {message}")
    
    def _broadcast_to_telegram(self, message: str) -> None:
        """
        Send message to Telegram channel if enabled.
        
        Args:
            message: Message to send.
        """
        if not self.telegram_config.enabled:
            return
        
        try:
            response = self._send_telegram_message(message)
            if response is None:
                self.logger.warning("Failed to send Telegram message")
        except Exception as e:
            self.logger.error(f"Telegram API Error: {e}")
    
    def _send_telegram_message(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Send a message to the Telegram channel.
        
        Args:
            message: Message to send.
            
        Returns:
            Optional[Dict[str, Any]]: Response from Telegram API or None if failed.
        """
        if not self.telegram_config.enabled:
            return None
        
        headers = {
            "X-API-Key": self.telegram_config.api_key,
            "Content-Type": "application/json"
        }
        
        body = {
            "message": message,
            "channel_name": self.telegram_config.channel_name,
            "channel_secret": self.telegram_config.channel_secret
        }
        
        try:
            response = requests.post(
                self.telegram_config.api_url,
                headers=headers,
                json=body,
                timeout=10
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            raise NotificationError(f"Failed to send Telegram message: {e}")
    
    def test_telegram_connection(self) -> bool:
        """
        Test Telegram connection without sending actual messages.
        
        Returns:
            bool: True if connection is valid, False otherwise.
        """
        if not self.telegram_config.enabled:
            self.logger.info("Telegram notifications disabled - configuration incomplete")
            return False
        
        try:
            # Validate configuration format
            if not self.telegram_config.api_key or len(self.telegram_config.api_key) < 10:
                self.logger.error("Invalid Telegram API key format")
                return False
            
            if not self.telegram_config.api_url.startswith(('http://', 'https://')):
                self.logger.error("Invalid Telegram API URL format")
                return False
            
            if not self.telegram_config.channel_name or not self.telegram_config.channel_secret:
                self.logger.error("Missing Telegram channel configuration")
                return False
            
            self.logger.info("Telegram configuration valid - notifications enabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Telegram configuration error: {e}")
            return False
    
    def get_telegram_status(self) -> str:
        """
        Get the current Telegram status.
        
        Returns:
            str: Status description.
        """
        if self.telegram_config.enabled:
            return f"enabled for channel {self.telegram_config.channel_name}"
        else:
            return "disabled"
    
    def log_email_moved(self, subject: str, sender: str, date_received: str, 
                       reason: str, success: bool = True) -> None:
        """
        Log details about an email being moved to Gelesen folder.
        
        Args:
            subject: Email subject.
            sender: Email sender.
            date_received: Date email was received.
            reason: Reason for moving the email.
            success: Whether the operation was successful.
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_message = (
                f"📧 EMAIL MOVED TO GELESEN | "
                f"Timestamp: {timestamp} | "
                f"Subject: {subject} | "
                f"Sender: {sender} | "
                f"Date Received: {date_received} | "
                f"Reason: {reason} | "
                f"Status: {'SUCCESS' if success else 'FAILED'}"
            )
            
            self.log_info(log_message)
            
        except Exception as e:
            self.log_error(f"Error logging email details: {e}")
