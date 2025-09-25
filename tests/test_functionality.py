"""
Test functionality for Netflix Autovalidator
Tests logging, Telegram connection, and other core functions
"""

import os
import requests
import logging
import ssl
from datetime import datetime
from dotenv import load_dotenv
from imap_tools import MailBox

def test_logging_functionality(logger, log_path):
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
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "DEBUG":
            logger.debug(message)
    
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

def test_telegram_connection(telegram_api_key, telegram_api_url, telegram_channel_name, telegram_channel_secret):
    """Test Telegram connection configuration without sending actual messages"""
    if not all([telegram_api_key, telegram_api_url, telegram_channel_name, telegram_channel_secret]):
        print("⚠️ Telegram configuration incomplete - notifications disabled")
        return False
    
    # Test configuration validity without sending actual messages
    try:
        # Just validate the configuration format
        if not telegram_api_key or len(telegram_api_key) < 10:
            print("❌ Invalid Telegram API key format - notifications disabled")
            return False
        
        if not telegram_api_url.startswith(('http://', 'https://')):
            print("❌ Invalid Telegram API URL format - notifications disabled")
            return False
        
        if not telegram_channel_name or not telegram_channel_secret:
            print("❌ Missing Telegram channel configuration - notifications disabled")
            return False
        
        print("✅ Telegram configuration valid - notifications enabled")
        return True
        
    except Exception as e:
        print(f"❌ Telegram configuration error: {e} - notifications disabled")
        return False

def test_email_logging(log_email_moved_func):
    """Test email logging function with a mock email object"""
    print("🧪 Testing email logging function...")
    
    class MockEmail:
        def __init__(self):
            self.subject = "Test Email Subject"
            self.from_ = "test@example.com"
            self.date = datetime.now()
    
    mock_email = MockEmail()
    log_email_moved_func(mock_email, "Logging test - email moved")
    print("✅ Email logging test completed")

def test_log_and_broadcast(log_and_broadcast_func):
    """Test log_and_broadcast function"""
    print("🧪 Testing log_and_broadcast function...")
    log_and_broadcast_func("🔧 Logging test - log_and_broadcast function test", "INFO")
    print("✅ log_and_broadcast test completed")

def test_email_connection(email, password, imap_server, imap_port):
    """Test email IMAP connection and return True if successful, False otherwise"""
    print("🧪 Testing email IMAP connection...")
    
    if not all([email, password, imap_server, imap_port]):
        print("❌ Email configuration incomplete - missing credentials or server settings")
        return False
    
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        # Test connection
        with MailBox(imap_server, port=imap_port, ssl_context=ssl_context).login(email, password) as mailbox:
            # Get folder list to verify connection works
            folders = [f.name for f in mailbox.folder.list()]
            print(f"✅ Email connection successful!")
            print(f"📁 Available folders: {len(folders)} folders found")
            print(f"📧 Connected as: {email}")
            print(f"🌐 Server: {imap_server}:{imap_port}")
            
            # Check if Gelesen folder exists, if not, mention it will be created
            gelesen_folder = "Gelesen"
            if gelesen_folder in folders:
                print(f"✅ '{gelesen_folder}' folder found")
            else:
                print(f"ℹ️ '{gelesen_folder}' folder not found - will be created when needed")
            
            return True
            
    except Exception as e:
        print(f"❌ Email connection failed: {e}")
        print("💡 Please check your email credentials and IMAP server settings")
        return False

def run_all_tests(logger, log_path, telegram_config, email_config, log_email_moved_func, log_and_broadcast_func):
    """Run all tests with provided configuration and functions"""
    print("🚀 Starting comprehensive functionality tests...")
    
    # Test logging
    test_logging_functionality(logger, log_path)
    
    # Test log_and_broadcast
    test_log_and_broadcast(log_and_broadcast_func)
    
    # Test email logging
    test_email_logging(log_email_moved_func)
    
    # Test email connection
    email_enabled = test_email_connection(
        email_config['email'],
        email_config['password'],
        email_config['imap_server'],
        email_config['imap_port']
    )
    
    # Test Telegram connection
    telegram_enabled = test_telegram_connection(
        telegram_config['api_key'],
        telegram_config['api_url'],
        telegram_config['channel_name'],
        telegram_config['channel_secret']
    )
    
    print("✅ All functionality tests completed")
    print(f"📊 Email connection: {'✅ Enabled' if email_enabled else '❌ Disabled'}")
    print(f"📊 Telegram notifications: {'✅ Enabled' if telegram_enabled else '❌ Disabled'}")
    
    return telegram_enabled, email_enabled
