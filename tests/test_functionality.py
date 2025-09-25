"""
Test functionality for Netflix Autovalidator
Tests logging, Telegram connection, and other core functions using the new modular structure
"""

import os
from datetime import datetime
from config import Config
from notifications import NotificationHandler
from email_handler import EmailHandler, EmailConnectionError


def test_logging_functionality(notification_handler: NotificationHandler, log_path: str) -> None:
    """Test logging functionality for both file and console output"""
    print("🧪 Testing logging functionality...")
    
    # Test different log levels
    test_messages = [
        ("INFO", "📝 Logging test - INFO level message"),
        ("WARNING", "⚠️ Logging test - WARNING level message"),
        ("ERROR", "❌ Logging test - ERROR level message"),
        ("DEBUG", "🔍 Logging test - DEBUG level message")
    ]
    
    for level, message in test_messages:
        if level == "INFO":
            notification_handler.log_info(message)
        elif level == "WARNING":
            notification_handler.log_warning(message)
        elif level == "ERROR":
            notification_handler.log_error(message)
        elif level == "DEBUG":
            notification_handler.log_debug(message)
    
    # Test file logging by checking if log file exists and has content
    try:
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
                if "Logging test" in log_content:
                    print("✅ File logging test successful")
                else:
                    print("❌ File logging test failed - no test messages found in log file")
        else:
            print(f"❌ Log file not found at {log_path}")
    except Exception as e:
        print(f"❌ Error testing file logging: {e}")
    
    print("✅ Logging functionality test completed")


def test_telegram_connection(notification_handler: NotificationHandler) -> bool:
    """Test Telegram connection configuration without sending actual messages"""
    print("🧪 Testing Telegram connection...")
    
    try:
        result = notification_handler.test_telegram_connection()
        if result:
            print("✅ Telegram configuration valid - notifications enabled")
        else:
            print("⚠️ Telegram configuration invalid - notifications disabled")
        return result
    except Exception as e:
        print(f"❌ Telegram configuration error: {e} - notifications disabled")
        return False


def test_email_logging(notification_handler: NotificationHandler) -> None:
    """Test email logging function with mock data"""
    print("🧪 Testing email logging function...")
    
    try:
        notification_handler.log_email_moved(
            subject="Test Email Subject",
            sender="test@example.com",
            date_received=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            reason="Logging test - email moved",
            success=True
        )
        print("✅ Email logging test completed")
    except Exception as e:
        print(f"❌ Email logging test failed: {e}")


def test_notification_functions(notification_handler: NotificationHandler) -> None:
    """Test notification functions"""
    print("🧪 Testing notification functions...")
    
    try:
        notification_handler.log_and_broadcast("🔧 Logging test - notification function test", "INFO")
        print("✅ Notification functions test completed")
    except Exception as e:
        print(f"❌ Notification functions test failed: {e}")


def test_email_connection(email_handler: EmailHandler) -> bool:
    """Test email IMAP connection and return True if successful, False otherwise"""
    print("🧪 Testing email IMAP connection...")
    
    try:
        # Test connection
        import asyncio
        asyncio.run(email_handler.connect())
        
        # Get folder list to verify connection works
        if email_handler.mailbox:
            folders = [f.name for f in email_handler.mailbox.folder.list()]
            print(f"✅ Email connection successful!")
            print(f"📁 Available folders: {len(folders)} folders found")
            print(f"📧 Connected as: {email_handler.email_config.email}")
            print(f"🌐 Server: {email_handler.email_config.imap_server}:{email_handler.email_config.imap_port}")
            
            # Check if Gelesen folder exists, if not, mention it will be created
            gelesen_folder = email_handler.app_config.gelesen_folder
            if gelesen_folder in folders:
                print(f"✅ '{gelesen_folder}' folder found")
            else:
                print(f"ℹ️ '{gelesen_folder}' folder not found - will be created when needed")
            
            # Disconnect
            asyncio.run(email_handler.disconnect())
            return True
        else:
            print("❌ Email connection failed - no mailbox connection")
            return False
            
    except EmailConnectionError as e:
        print(f"❌ Email connection failed: {e}")
        print("💡 Please check your email credentials and IMAP server settings")
        return False
    except Exception as e:
        print(f"❌ Email connection failed: {e}")
        print("💡 Please check your email credentials and IMAP server settings")
        return False


def run_all_tests(config: Config, notification_handler: NotificationHandler, email_handler: EmailHandler) -> tuple[bool, bool]:
    """Run all tests with the new modular structure"""
    print("🚀 Starting comprehensive functionality tests...")
    
    # Test logging
    test_logging_functionality(notification_handler, config.app.log_path)
    
    # Test notification functions
    test_notification_functions(notification_handler)
    
    # Test email logging
    test_email_logging(notification_handler)
    
    # Test email connection
    email_enabled = test_email_connection(email_handler)
    
    # Test Telegram connection
    telegram_enabled = test_telegram_connection(notification_handler)
    
    print("✅ All functionality tests completed")
    print(f"📊 Email connection: {'✅ Enabled' if email_enabled else '❌ Disabled'}")
    print(f"📊 Telegram notifications: {'✅ Enabled' if telegram_enabled else '❌ Disabled'}")
    
    return telegram_enabled, email_enabled
