import asyncio
import os
from dotenv import load_dotenv
import ssl
from imap_tools import MailBox
from playwright.async_api import async_playwright
import time
import logging
from datetime import datetime, timezone
import requests
import re

load_dotenv("config.env")

GELESEN_FOLDER = "Gelesen"
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
LOG_PATH = os.getenv("LOG_PATH", "netflix-validator.log")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY", "asdfghjkl")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL", "http://localhost:5000/api/broadcast-to-channel")
TELEGRAM_CHANNEL_NAME = os.getenv("TELEGRAM_CHANNEL_NAME", "roy")
TELEGRAM_CHANNEL_SECRET = os.getenv("TELEGRAM_CHANNEL_SECRET", "a55ed20e2")
CHECK_INTERVAL = 20  # seconds
MINUTES_TO_WAIT = 900 # 900 seconds = 15 minutes
MAX_RETRY_ATTEMPTS = 3  # Maximum retry attempts before giving up

retry_count = 0

# Configure logging
log_dir = os.path.dirname(LOG_PATH)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

SSL_CONTEXT = ssl.create_default_context()

def log_email_moved(msg, reason, success=True):
    """Log details about an email being moved to gelesen folder"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = msg.subject or "No Subject"
        sender = msg.from_ or "Unknown Sender"
        date_received = msg.date.strftime("%Y-%m-%d %H:%M:%S") if msg.date else "Unknown Date"
        
        log_message = (
            f"📧 EMAIL MOVED TO GELESEN | "
            f"Timestamp: {timestamp} | "
            f"Subject: {subject} | "
            f"Sender: {sender} | "
            f"Date Received: {date_received} | "
            f"Reason: {reason} | "
            f"Status: {'SUCCESS' if success else 'FAILED'}"
        )
        
        logger.info(log_message)
        print(log_message)
        
    except Exception as e:
        logger.error(f"Error logging email details: {e}")

async def click_verification_code_link(url):
    logger.info(f"🌍 Opening link: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector('[data-uia="travel-verification-otp"]', timeout=5000)
        verification_code = await page.inner_text('[data-uia="travel-verification-otp"]', timeout=5000)
        await browser.close()
        if verification_code:
            log_and_broadcast(f"🔢 Verification code: {verification_code}")
            return verification_code
        else:
            log_and_broadcast(f"❌ No verification code found")
            return False
        
async def click_confirmation_link(url):
    logger.info(f"🌍 Opening link: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector('[data-uia="set-primary-location-action"]', timeout=5000)
        
        # Wait for a confirmation message or page change to verify success
        response = await page.goto(url)
        await browser.close()
        if response and response.status == 200:
            log_and_broadcast("✅ Confirmation link clicked successfully!")
        else:
            logger.warning(f"⚠️ Loading error. Status: {response.status if response else 'No response'}")
            return False
        return True

async def check_emails(mailbox):
    """Check emails using existing mailbox connection"""
    try:
        print(f"📧 Checking for new emails...")
        current_time = datetime.now(timezone.utc)
        
        for msg in mailbox.fetch(reverse=True):
            try:
                html = msg.html or msg.text
                
                # Check if email is older than 15 minutes AND has been read
                if msg.date:
                    time_diff = current_time - msg.date
                    if time_diff.total_seconds() > MINUTES_TO_WAIT and msg.flags and '\\Seen' in msg.flags:
                        mailbox.move(msg.uid, GELESEN_FOLDER)
                        log_and_broadcast(f"📦 Email '{msg.subject}' moved to Gelesen (older than 15 minutes AND read)")
                        log_email_moved(msg, "Email older than 15 minutes AND read")
                        continue  # Skip further processing for this email
                    
                if "accountaccess" in html:
                    start = html.find("https://www.netflix.com/accountaccess")
                    end = html.find('"', start)
                    url = html[start:end]
                    
                    log_and_broadcast(f"✅ Found Netflix link!:\n{url}")
                    
                    # Extract verification code from HTML using Regex - look anywhere in HTML for 4-digit number
                    match = re.search(r'<td[^>]*>\s*(\d{4})\s*</td>', html)
                    if match:
                        verification_code = match.group(1)
                        log_and_broadcast(f"🔢 Verification code: {verification_code}")
                    else:
                        log_and_broadcast(f"❌ No verification code found")
                    
                    log_and_broadcast(f"📦 Email '{msg.subject}' moved to Gelesen")
                    mailbox.move(msg.uid, GELESEN_FOLDER)

                if "travel/verify" in html:
                    start = html.find("https://www.netflix.com/account/travel/verify")
                    end = html.find('"', start)
                    url = html[start:end]
                
                    log_and_broadcast(f"✅ Found Netflix link!:\n{url}")

                    # Extract verification code from HTML
                    verification_code_successful = await click_verification_code_link(url)
                    if verification_code_successful:
                        mailbox.move(msg.uid, GELESEN_FOLDER)
                        log_and_broadcast("📦 Email moved to Gelesen folder")
                        log_email_moved(msg, "Netflix verification code link clicked")
                    else:
                        log_and_broadcast(f"❌ No verification code found")
                      
                if "update-primary-location" in html:
                    start = html.find("https://www.netflix.com/account/update-primary-location")
                    end = html.find('"', start)
                    url = html[start:end]
                    
                    log_and_broadcast(f"✅ Found Netflix link!:\n{url}")

                    confirmation_successful = await click_confirmation_link(url)
                    
                    if confirmation_successful:
                        mailbox.move(msg.uid, GELESEN_FOLDER)
                        log_and_broadcast("📦 Email moved to Gelesen folder")
                        log_email_moved(msg, "Netflix update link clicked")
                    else:
                        log_and_broadcast("❌ Failed to click confirmation link, email not moved", "WARNING")
            except Exception as msg_error:
                # Log individual email processing errors but don't break the entire check
                logger.warning(f"⚠️ Error processing email '{msg.subject if hasattr(msg, 'subject') else 'Unknown'}': {msg_error}")
                continue
                
    except Exception as e:
        logger.error(f"❌ Error checking emails: {e}")
        # Only re-raise critical errors that require reconnection
        if "connection" in str(e).lower() or "timeout" in str(e).lower() or "ssl" in str(e).lower():
            raise
        else:
            # For other errors, just log and continue
            logger.warning(f"⚠️ Non-critical error, continuing: {e}")

def broadcast_to_channel(message):
    headers = {
        "X-API-Key": TELEGRAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    body = {
        "message": message,
        "channel_name": TELEGRAM_CHANNEL_NAME,
        "channel_secret": TELEGRAM_CHANNEL_SECRET
    }
    
    try:
        response = requests.post(TELEGRAM_API_URL, headers=headers, json=body)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"❌ API Error: {e}")
        return None

def log_and_broadcast(message, level="INFO"):
    """Log to file and broadcast to Telegram channel"""
    # Log to file
    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "DEBUG":
        logger.debug(message)
    
    # Broadcast to Telegram (only for important messages)
    if level in ["INFO", "ERROR", "WARNING"]:
        broadcast_to_channel(message)

async def establish_connection_and_check_emails():
    with MailBox(IMAP_SERVER, port=IMAP_PORT, ssl_context=SSL_CONTEXT).login(EMAIL, PASSWORD) as mailbox:
        log_and_broadcast(f"✅ Connected to mailbox successfully")
        while True:
            try:
                await check_emails(mailbox)
                logger.debug(f"💤 Waiting {CHECK_INTERVAL} seconds before next check...")
                await asyncio.sleep(CHECK_INTERVAL)
            except Exception as e:
                log_and_broadcast(f"❌ Error in check_emails: {e}", "ERROR")
                log_and_broadcast("🔄 Reconnecting...")
                # Add delay before reconnecting to prevent rapid reconnection loop
                await asyncio.sleep(CHECK_INTERVAL)
                break  # Break inner loop to reconnect

async def main():
    retry_count = 0

    print("🚀 Starting main function")
    log_and_broadcast(f"🔄 Starting Netflix Autovalidator - checking every {CHECK_INTERVAL} seconds")
    log_and_broadcast(f"📡 Connecting to {IMAP_SERVER}:{IMAP_PORT} as {EMAIL}")
    log_and_broadcast(f"📝 Logging to {LOG_PATH} and broadcasting to channel {TELEGRAM_CHANNEL_NAME}")
    

    while retry_count < MAX_RETRY_ATTEMPTS:
        try:
            await establish_connection_and_check_emails()
            # If we reach here, connection was successful, reset retry count
            retry_count = 0
                        
        except Exception as e:
            retry_count += 1
            log_and_broadcast(f"❌ Failed to connect (attempt {retry_count}/{MAX_RETRY_ATTEMPTS}): {e}", "ERROR")
            
            if retry_count >= MAX_RETRY_ATTEMPTS:
                log_and_broadcast(f"💀 Maximum retry attempts ({MAX_RETRY_ATTEMPTS}) reached. Shutting down gracefully.", "ERROR")
                log_and_broadcast("🛑 Netflix VerifyBot is stopping to prevent infinite loops and spam.", "ERROR")
                import sys
                sys.exit(0)  # Exit with code 0 for graceful shutdown
            else:
                # Use exponential backoff: wait longer between retries
                wait_time = CHECK_INTERVAL * (2 ** (retry_count - 1))  # 5, 10, 20 seconds
                log_and_broadcast(f"🔄 Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
    
    log_and_broadcast("👋 Netflix VerifyBot has stopped (retry count: {retry_count}).", "INFO")

asyncio.run(main())