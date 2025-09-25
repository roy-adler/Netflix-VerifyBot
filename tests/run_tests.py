#!/usr/bin/env python3
"""
Standalone test runner for Netflix Autovalidator
Can be run independently to test functionality without starting the main application
"""

import sys
import os
from config import load_config, validate_config, ConfigError
from notifications import NotificationHandler
from email_handler import EmailHandler
from .test_functionality import run_all_tests

def setup_test_environment():
    """Setup test environment using the new modular structure"""
    try:
        # Load configuration using the new config module
        config = load_config()
        validate_config(config)
        
        # Create notification handler
        notification_handler = NotificationHandler(config.telegram, config.app.log_path)
        
        # Create email handler
        email_handler = EmailHandler(config.email, config.app, notification_handler)
        
        return config, notification_handler, email_handler
        
    except ConfigError as e:
        print(f"❌ Configuration error: {e}")
        return None, None, None
    except Exception as e:
        print(f"❌ Error setting up test environment: {e}")
        return None, None, None

def main():
    """Run all tests independently"""
    print("🧪 Running Netflix Autovalidator Pre-Startup Tests...")
    print("=" * 60)
    
    try:
        # Setup test environment
        config, notification_handler, email_handler = setup_test_environment()
        
        if not config:
            print("❌ Failed to setup test environment")
            return 1
        
        # Run all tests using the new modular structure
        telegram_enabled, email_enabled = run_all_tests(
            config,
            notification_handler,
            email_handler
        )
        
        print("=" * 60)
        print(f"✅ All pre-startup tests completed!")
        print(f"📊 Email connection: {'✅ Enabled' if email_enabled else '❌ Disabled'}")
        print(f"📊 Telegram notifications: {'✅ Enabled' if telegram_enabled else '❌ Disabled'}")
        print(f"📝 Log file: {config.app.log_path}")
        
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
