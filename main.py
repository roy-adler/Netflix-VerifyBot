import asyncio
import os
import sys
import socket
from dotenv import load_dotenv
import ssl
from imap_tools import MailBox
from playwright.async_api import async_playwright
import logging
from datetime import datetime, timezone
import requests
import re

# Load environment variables before reading them
load_dotenv("config.env")

# Global constants
GELESEN_FOLDER = "Gelesen"
CHECK_INTERVAL = 1  # seconds
MINUTES_TO_WAIT = 900  # 900 seconds = 15 minutes
MAX_RETRY_ATTEMPTS = 3
CONNECTION_REFRESH_INTERVAL = 3600  # 3600 seconds = 1 hour
SSL_CONTEXT = ssl.create_default_context()
socket.setdefaulttimeout(30)

# Global variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
LOG_PATH = os.getenv("LOG_PATH", "netflix-validator.log")
TELEGRAM_CHANNEL_BOT_API_KEY = os.getenv("TELEGRAM_CHANNEL_BOT_API_KEY")
TELEGRAM_CHANNEL_BOT_API_URL = os.getenv("TELEGRAM_CHANNEL_BOT_API_URL")
TELEGRAM_CHANNEL_NAME = os.getenv("TELEGRAM_CHANNEL_NAME")
TELEGRAM_CHANNEL_SECRET = os.getenv("TELEGRAM_CHANNEL_SECRET")
TELEGRAM_INFO_CHANNEL_NAME = os.getenv("TELEGRAM_INFO_CHANNEL_NAME")
TELEGRAM_INFO_CHANNEL_SECRET = os.getenv("TELEGRAM_INFO_CHANNEL_SECRET")
TELEGRAM_ENABLED = bool(
    TELEGRAM_CHANNEL_BOT_API_KEY
    and TELEGRAM_CHANNEL_BOT_API_URL
    and TELEGRAM_CHANNEL_NAME
    and TELEGRAM_CHANNEL_SECRET
)
logger = None
connection_start_time = None


def setup_application():
    """Initialize application logging"""
    global logger

    log_dir = os.path.dirname(LOG_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger(__name__)
    return logger


def log_email_moved(msg, reason, success=True):
    """Log details about an email being moved to gelesen folder"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = msg.subject or "No Subject"
        sender = msg.from_ or "Unknown Sender"
        date_received = (
            msg.date.strftime("%Y-%m-%d %H:%M:%S") if msg.date else "Unknown Date"
        )

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

    except Exception as e:
        logger.error(f"Error logging email details: {e}")


async def click_verification_code_link(url):
    logger.info(f"🌍 Opening link: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector(
            '[data-uia="travel-verification-otp"]', timeout=5000
        )
        verification_code = await page.inner_text(
            '[data-uia="travel-verification-otp"]', timeout=5000
        )
        await browser.close()
        if verification_code:
            log_and_broadcast(
                f"| Account Access from Phone/Tablet | \n 🔢 Verification code: {verification_code}",
                public=True,
            )
            return verification_code
        else:
            log_and_broadcast("❌ No verification code found", public=True)
            return False


async def click_confirmation_link(url):
    logger.info(f"🌍 Opening link: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        response = await page.goto(url)
        if not response or response.status != 200:
            logger.warning(
                f"⚠️ Failed to load page. Status: {response.status if response else 'No response'}"
            )
            await browser.close()
            return False

        await page.wait_for_selector(
            '[data-uia="set-primary-location-action"]', timeout=5000
        )
        await page.click('[data-uia="set-primary-location-action"]', timeout=5000)
        log_and_broadcast("✅ Confirmation link clicked successfully!")

        await page.wait_for_timeout(2000)

        current_url = page.url
        logger.info(f"📍 Current page after click: {current_url}")

        await browser.close()
        return True


def _extract_url(html, pattern):
    """Extract a URL from HTML using regex."""
    match = re.search(pattern, html)
    return match.group(0) if match else None


async def check_emails(mailbox):
    """Check emails using existing mailbox connection"""
    try:
        print("📧 Checking for new emails...")
        current_time = datetime.now(timezone.utc)

        for msg in mailbox.fetch(reverse=True):
            try:
                html = msg.html or msg.text

                # Check if email is older than 15 minutes AND has been read
                if msg.date:
                    time_diff = current_time - msg.date
                    if (
                        time_diff.total_seconds() > MINUTES_TO_WAIT
                        and msg.flags
                        and "\\Seen" in msg.flags
                    ):
                        mailbox.move(msg.uid, GELESEN_FOLDER)
                        log_and_broadcast(
                            f"📦 Email '{msg.subject}' moved to Gelesen (older than 15 minutes AND read)"
                        )
                        log_email_moved(msg, "Email older than 15 minutes AND read")
                        continue

                if "accountaccess" in html:
                    url = _extract_url(
                        html, r'https://www\.netflix\.com/accountaccess[^"\s>]+'
                    )
                    if url:
                        log_and_broadcast(f"✅ Found Netflix link!:\n{url}")

                        match = re.search(r"<td[^>]*>\s*(\d{4})\s*</td>", html)
                        if match:
                            verification_code = match.group(1)
                            log_and_broadcast(
                                f"| New login verification code| \n🔢 Verification code: {verification_code}",
                                public=True,
                            )
                        else:
                            log_and_broadcast(
                                "❌ No verification code found", public=True
                            )

                        log_and_broadcast(
                            f"📦 Email '{msg.subject}' moved to Gelesen"
                        )
                        mailbox.move(msg.uid, GELESEN_FOLDER)

                if "travel/verify" in html:
                    url = _extract_url(
                        html,
                        r'https://www\.netflix\.com/account/travel/verify[^"\s>]+',
                    )
                    if url:
                        log_and_broadcast(f"✅ Found Netflix link!:\n{url}")

                        verification_code_successful = (
                            await click_verification_code_link(url)
                        )
                        if verification_code_successful:
                            mailbox.move(msg.uid, GELESEN_FOLDER)
                            log_and_broadcast("📦 Email moved to Gelesen folder")
                            log_email_moved(
                                msg, "Netflix verification code link clicked"
                            )
                        else:
                            log_and_broadcast("❌ No verification code found")

                if "update-primary-location" in html:
                    url = _extract_url(
                        html,
                        r'https://www\.netflix\.com/account/update-primary-location[^"\s>]+',
                    )
                    if url:
                        log_and_broadcast(
                            f"| Update primary location | \n✅ Found Netflix link!:\n{url}",
                            public=True,
                        )

                        confirmation_successful = await click_confirmation_link(url)

                        if confirmation_successful:
                            mailbox.move(msg.uid, GELESEN_FOLDER)
                            log_and_broadcast("📦 Email moved to Gelesen folder")
                            log_email_moved(msg, "Netflix update link clicked")
                        else:
                            log_and_broadcast(
                                "❌ Failed to click confirmation link, email not moved",
                                "WARNING",
                                public=True,
                            )

            except Exception as msg_error:
                logger.warning(
                    f"⚠️ Error processing email '{msg.subject if hasattr(msg, 'subject') else 'Unknown'}': {msg_error}"
                )
                continue

    except Exception as e:
        logger.error(f"❌ Error checking emails: {e}")
        if any(
            keyword in str(e).lower()
            for keyword in ["connection", "timeout", "ssl", "eof", "closed"]
        ):
            raise
        else:
            logger.warning(f"⚠️ Non-critical error, continuing: {e}")


def broadcast_to_channel(message, public=False):
    """Send message to Telegram channel(s) if enabled"""
    if not TELEGRAM_ENABLED:
        return None

    headers = {
        "X-API-Key": TELEGRAM_CHANNEL_BOT_API_KEY,
        "Content-Type": "application/json",
    }

    info_body = {
        "message": message,
        "channel_name": TELEGRAM_INFO_CHANNEL_NAME,
        "channel_secret": TELEGRAM_INFO_CHANNEL_SECRET,
    }

    try:
        response = requests.post(
            TELEGRAM_CHANNEL_BOT_API_URL, headers=headers, json=info_body, timeout=10
        )

        if public:
            public_body = {
                "message": message,
                "channel_name": TELEGRAM_CHANNEL_NAME,
                "channel_secret": TELEGRAM_CHANNEL_SECRET,
            }
            response = requests.post(
                TELEGRAM_CHANNEL_BOT_API_URL,
                headers=headers,
                json=public_body,
                timeout=10,
            )

        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"❌ Telegram API Error: {e}")
        return None


def log_and_broadcast(message, level="INFO", public=False):
    """Log to file and broadcast to Telegram channel"""
    if logger is not None:
        if level == "INFO":
            logger.info(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "DEBUG":
            logger.debug(message)
    else:
        print(f"[{level}] {message}")

    if level in ["INFO", "ERROR", "WARNING"]:
        broadcast_to_channel(message, public)


async def establish_connection_and_check_emails():
    global connection_start_time

    logger.info(f"📡 Connecting to {IMAP_SERVER}:{IMAP_PORT} as {EMAIL}")

    mailbox = MailBox(IMAP_SERVER, port=IMAP_PORT, ssl_context=SSL_CONTEXT).login(
        EMAIL, PASSWORD
    )
    try:
        connection_start_time = datetime.now()
        logger.info("✅ Connected to mailbox successfully")

        while True:
            current_time = datetime.now()
            if (
                current_time - connection_start_time
            ).total_seconds() >= CONNECTION_REFRESH_INTERVAL:
                logger.info(
                    "🔄 Connection refresh needed (1 hour reached) - reconnecting..."
                )
                return

            await check_emails(mailbox)
            await asyncio.sleep(CHECK_INTERVAL)
    finally:
        try:
            mailbox.logout()
            logger.info("📤 Mailbox connection closed")
        except Exception as e:
            logger.warning(f"⚠️ Error closing mailbox connection: {e}")


async def main():
    log_and_broadcast("Testing application configuration...")

    try:
        from tests.run_tests import main as run_tests_main

        test_exit_code = run_tests_main()
        if test_exit_code != 0:
            print("❌ Pre-startup tests failed! Application will not start.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error running pre-startup tests: {e}")
        sys.exit(1)

    log_and_broadcast("Testing successful!")

    setup_application()

    log_and_broadcast(
        f"🔄 Starting Netflix Autovalidator - checking every {CHECK_INTERVAL} seconds"
    )

    telegram_status = "enabled" if TELEGRAM_ENABLED else "disabled"
    log_and_broadcast(
        f"📝 Logging to {LOG_PATH} and Telegram notifications {telegram_status} for channel {TELEGRAM_CHANNEL_NAME}"
    )

    retry_count = 0
    last_error = None  # Holds error from first disconnect to check if it was transient

    while retry_count < MAX_RETRY_ATTEMPTS:
        try:
            await establish_connection_and_check_emails()

            # Reconnect succeeded — check if we just recovered from a brief disconnection
            if last_error is not None:
                log_and_broadcast(
                    f"⚡ Brief disconnection, reconnected successfully (was: {last_error})"
                )
                last_error = None

            retry_count = 0

        except Exception as e:
            retry_count += 1
            last_error = str(e)

            if retry_count == 1:
                # First failure — could be transient (e.g. server restart at midnight)
                # Log to file only and silently retry before alarming
                logger.warning(
                    f"⚠️ Connection dropped, retrying silently (attempt {retry_count}/{MAX_RETRY_ATTEMPTS}): {e}"
                )
            else:
                # Second+ failure in a row — this is a real problem
                log_and_broadcast(
                    f"❌ Persistent connection issue (attempt {retry_count}/{MAX_RETRY_ATTEMPTS}): {e}",
                    "ERROR",
                )

            if retry_count >= MAX_RETRY_ATTEMPTS:
                log_and_broadcast(
                    f"💀 Maximum retry attempts ({MAX_RETRY_ATTEMPTS}) reached. Shutting down gracefully.",
                    "ERROR",
                )
                log_and_broadcast(
                    "🛑 Netflix VerifyBot is stopping to prevent infinite loops and spam.",
                    "ERROR",
                )
                sys.exit(0)
            else:
                wait_time = CHECK_INTERVAL * (2 ** (retry_count - 1))
                logger.info(f"🔄 Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

    log_and_broadcast(
        f"👋 Netflix VerifyBot has stopped (retry count: {retry_count}).", "INFO"
    )


asyncio.run(main())
