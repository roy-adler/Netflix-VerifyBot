#!/usr/bin/env python3
"""
Standalone test runner for Netflix Autovalidator
Can be run independently to test functionality without starting the main application
"""

import os
import logging
from dotenv import load_dotenv
from .test_functionality import run_all_tests

def setup_test_environment():
    """Setup test environment similar to main application"""
    # Load environment variables
    load_dotenv("config.env")
    
    # Get configuration
    log_path = os.getenv("LOG_PATH", "netflix-validator.log")
    telegram_config = {
        'api_key': os.getenv("TELEGRAM_API_KEY"),
        'api_url': os.getenv("TELEGRAM_API_URL"),
        'channel_name': os.getenv("TELEGRAM_CHANNEL_NAME"),
        'channel_secret': os.getenv("TELEGRAM_CHANNEL_SECRET")
    }
    
    email_config = {
        'email': os.getenv("EMAIL"),
        'password': os.getenv("PASSWORD"),
        'imap_server': os.getenv("IMAP_SERVER"),
        'imap_port': int(os.getenv("IMAP_PORT", "993"))
    }
    
    # Setup logging
    log_dir = os.path.dirname(log_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    return logger, log_path, telegram_config, email_config

def mock_log_email_moved(msg, reason, success=True):
    """Mock function for testing email logging"""
    print(f"📧 Mock email logging: {reason} - {msg.subject}")

def mock_log_and_broadcast(message, level="INFO"):
    """Mock function for testing log_and_broadcast"""
    print(f"📢 Mock broadcast ({level}): {message}")

def main():
    """Run all tests independently"""
    print("🧪 Running Netflix Autovalidator Pre-Startup Tests...")
    print("=" * 60)
    
    try:
        # Setup test environment
        logger, log_path, telegram_config, email_config = setup_test_environment()
        
        # Run all tests
        telegram_enabled, email_enabled = run_all_tests(
            logger, 
            log_path, 
            telegram_config,
            email_config,
            mock_log_email_moved, 
            mock_log_and_broadcast
        )
        
        print("=" * 60)
        print(f"✅ All pre-startup tests completed!")
        print(f"📊 Email connection: {'✅ Enabled' if email_enabled else '❌ Disabled'}")
        print(f"📊 Telegram notifications: {'✅ Enabled' if telegram_enabled else '❌ Disabled'}")
        print(f"📝 Log file: {log_path}")
        
        # Fail if critical services are unavailable
        if not email_enabled:
            print("❌ Email connection failed - this is required for the application to work")
            print("💡 Please check your email credentials and IMAP server settings")
            return 1
        
        print("🚀 Application is ready to start!")
        return 0
        
    except Exception as e:
        print(f"❌ Pre-startup test failed with error: {e}")
        print("💡 Please check your configuration and try again")
        return 1

if __name__ == "__main__":
    exit(main())
