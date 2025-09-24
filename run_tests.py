#!/usr/bin/env python3
"""
Standalone test runner for Netflix Autovalidator
Can be run independently to test functionality without starting the main application
"""

import os
import logging
from dotenv import load_dotenv
from test_functionality import run_all_tests

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
    print("🧪 Running Netflix Autovalidator Tests...")
    print("=" * 50)
    
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
        
        print("=" * 50)
        print(f"✅ All tests completed successfully!")
        print(f"📊 Email connection: {'✅ Enabled' if email_enabled else '❌ Disabled'}")
        print(f"📊 Telegram notifications: {'✅ Enabled' if telegram_enabled else '❌ Disabled'}")
        print(f"📝 Log file: {log_path}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
