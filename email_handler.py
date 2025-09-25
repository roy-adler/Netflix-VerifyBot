"""
Email handling module for Netflix VerifyBot.

This module provides functionality for connecting to IMAP servers,
processing emails, and managing email operations.
"""

import asyncio
import socket
from typing import List, Optional, Iterator, Tuple
from datetime import datetime, timezone
from imap_tools import MailBox, MailMessage
from imap_tools.errors import MailboxFolderSelectError

from config import EmailConfig, AppConfig
from notifications import NotificationHandler


class EmailConnectionError(Exception):
    """Raised when there's an error connecting to the email server."""
    pass


class EmailProcessingError(Exception):
    """Raised when there's an error processing emails."""
    pass


class EmailHandler:
    """Handles all email-related operations."""
    
    def __init__(self, email_config: EmailConfig, app_config: AppConfig, 
                 notification_handler: NotificationHandler):
        """
        Initialize the email handler.
        
        Args:
            email_config: Email configuration settings.
            app_config: Application configuration settings.
            notification_handler: Handler for notifications and logging.
        """
        self.email_config = email_config
        self.app_config = app_config
        self.notification_handler = notification_handler
        self.mailbox: Optional[MailBox] = None
        self._connection_timeout = 30
        self._processed_emails: set = set()  # Track processed emails to prevent duplicates
    
    async def connect(self) -> None:
        """
        Establish connection to the email server.
        
        Raises:
            EmailConnectionError: If connection fails.
        """
        try:
            # Set socket timeout to prevent hanging connections
            socket.setdefaulttimeout(self._connection_timeout)
            
            self.notification_handler.log_info(
                f"📡 Connecting to {self.email_config.imap_server}:{self.email_config.imap_port} as {self.email_config.email}"
            )
            
            self.mailbox = MailBox(
                self.email_config.imap_server,
                port=self.email_config.imap_port,
                ssl_context=self.email_config.ssl_context
            ).login(self.email_config.email, self.email_config.password)
            
            self.notification_handler.log_info("✅ Connected to mailbox successfully")
            
        except Exception as e:
            raise EmailConnectionError(f"Failed to connect to email server: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the email server."""
        if self.mailbox:
            try:
                self.mailbox.logout()
                self.notification_handler.log_info("📤 Disconnected from email server")
            except Exception as e:
                self.notification_handler.log_warning(f"Warning during disconnect: {e}")
            finally:
                self.mailbox = None
    
    def is_connected(self) -> bool:
        """Check if connected to email server."""
        return self.mailbox is not None
    
    async def check_emails(self) -> None:
        """
        Check for new emails and process them.
        
        Raises:
            EmailProcessingError: If email processing fails.
        """
        if not self.is_connected():
            raise EmailProcessingError("Not connected to email server")
        
        try:
            self.notification_handler.log_debug("📧 Checking for new emails...")
            current_time = datetime.now(timezone.utc)
            
            for msg in self.mailbox.fetch(reverse=True):
                try:
                    await self._process_email(msg, current_time)
                except Exception as e:
                    self.notification_handler.log_warning(
                        f"⚠️ Error processing email '{getattr(msg, 'subject', 'Unknown')}': {e}"
                    )
                    continue
                    
        except Exception as e:
            # Re-raise critical errors that require reconnection
            if any(keyword in str(e).lower() for keyword in ["connection", "timeout", "ssl"]):
                raise EmailProcessingError(f"Critical email error: {e}")
            else:
                self.notification_handler.log_warning(f"⚠️ Non-critical email error: {e}")
    
    async def _process_email(self, msg: MailMessage, current_time: datetime) -> None:
        """
        Process a single email message.
        
        Args:
            msg: Email message to process.
            current_time: Current UTC time for age calculations.
        """
        # Check if email has already been processed to prevent duplicates
        email_id = f"{msg.uid}_{msg.date}_{msg.subject}" if msg.uid and msg.date and msg.subject else str(msg.uid)
        if email_id in self._processed_emails:
            self.notification_handler.log_debug(f"📧 Email already processed, skipping: {msg.subject}")
            return
        
        html = msg.html or msg.text
        
        # Check if email should be moved to Gelesen folder due to age and read status
        if self._should_move_old_email(msg, current_time):
            await self._move_email_to_gelesen(msg, "Email older than 15 minutes AND read")
            self._processed_emails.add(email_id)
            return
        
        # Process different types of Netflix emails
        if "accountaccess" in html:
            await self._process_account_access_email(msg, html)
            self._processed_emails.add(email_id)
        elif "travel/verify" in html:
            await self._process_travel_verify_email(msg, html)
            self._processed_emails.add(email_id)
        elif "update-primary-location" in html:
            await self._process_update_location_email(msg, html)
            self._processed_emails.add(email_id)
    
    def _should_move_old_email(self, msg: MailMessage, current_time: datetime) -> bool:
        """
        Check if email should be moved to Gelesen folder due to age and read status.
        
        Args:
            msg: Email message to check.
            current_time: Current UTC time.
            
        Returns:
            bool: True if email should be moved.
        """
        if not msg.date:
            return False
        
        time_diff = current_time - msg.date
        is_old = time_diff.total_seconds() > self.app_config.minutes_to_wait
        is_read = msg.flags and '\\Seen' in msg.flags
        
        return is_old and is_read
    
    async def _move_email_to_gelesen(self, msg: MailMessage, reason: str) -> None:
        """
        Move email to Gelesen folder and log the action.
        
        Args:
            msg: Email message to move.
            reason: Reason for moving the email.
        """
        try:
            # Check if mailbox is still connected
            if not self.is_connected():
                self.notification_handler.log_error("Cannot move email: not connected to mailbox")
                self._log_email_moved(msg, reason, success=False)
                return
            
            # Attempt to move the email
            self.mailbox.move(msg.uid, self.app_config.gelesen_folder)
            self.notification_handler.log_info(
                f"📦 Email '{msg.subject}' moved to Gelesen ({reason})"
            )
            self._log_email_moved(msg, reason, success=True)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "already moved" in error_msg or "not found" in error_msg:
                # Email was already moved or doesn't exist - this is not an error
                self.notification_handler.log_debug(f"Email already moved or not found: {msg.subject}")
                self._log_email_moved(msg, reason, success=True)
            else:
                self.notification_handler.log_error(f"Failed to move email: {e}")
                self._log_email_moved(msg, reason, success=False)
    
    async def _process_account_access_email(self, msg: MailMessage, html: str) -> None:
        """
        Process account access email with verification code.
        
        Args:
            msg: Email message to process.
            html: HTML content of the email.
        """
        url = self._extract_netflix_url(html, "https://www.netflix.com/accountaccess")
        if not url:
            return
        
        self.notification_handler.log_info(f"✅ Found Netflix link!:\n{url}")
        
        # Extract verification code from HTML
        verification_code = self._extract_verification_code_from_html(html)
        if verification_code:
            self.notification_handler.log_info(f"🔢 Verification code: {verification_code}")
        else:
            self.notification_handler.log_warning("❌ No verification code found")
        
        await self._move_email_to_gelesen(msg, "Netflix account access email processed")
    
    async def _process_travel_verify_email(self, msg: MailMessage, html: str) -> None:
        """
        Process travel verification email.
        
        Args:
            msg: Email message to process.
            html: HTML content of the email.
        """
        url = self._extract_netflix_url(html, "https://www.netflix.com/account/travel/verify")
        if not url:
            return
        
        self.notification_handler.log_info(f"✅ Found Netflix link!:\n{url}")
        
        # Use web scraper to get verification code
        from web_scraper import WebScrapingManager
        web_scraper = WebScrapingManager(self.notification_handler)
        verification_code = await web_scraper.process_verification_link(url)
        
        if verification_code:
            self.notification_handler.log_info(f"🔢 Verification code: {verification_code}")
            await self._move_email_to_gelesen(msg, "Netflix travel verification code extracted")
        else:
            self.notification_handler.log_warning("❌ No verification code found")
            await self._move_email_to_gelesen(msg, "Netflix travel verification email processed (no code found)")
    
    async def _process_update_location_email(self, msg: MailMessage, html: str) -> None:
        """
        Process update primary location email.
        
        Args:
            msg: Email message to process.
            html: HTML content of the email.
        """
        url = self._extract_netflix_url(html, "https://www.netflix.com/account/update-primary-location")
        if not url:
            return
        
        self.notification_handler.log_info(f"✅ Found Netflix link!:\n{url}")
        
        # Use web scraper to click confirmation link
        from web_scraper import WebScrapingManager
        web_scraper = WebScrapingManager(self.notification_handler)
        confirmation_successful = await web_scraper.process_confirmation_link(url)
        
        if confirmation_successful:
            self.notification_handler.log_info("✅ Confirmation link clicked successfully!")
            await self._move_email_to_gelesen(msg, "Netflix update location confirmation clicked")
        else:
            self.notification_handler.log_warning("❌ Failed to click confirmation link")
            await self._move_email_to_gelesen(msg, "Netflix update location email processed (confirmation failed)")
    
    def _extract_netflix_url(self, html: str, base_url: str) -> Optional[str]:
        """
        Extract Netflix URL from HTML content.
        
        Args:
            html: HTML content to search.
            base_url: Base URL to search for.
            
        Returns:
            Optional[str]: Extracted URL or None if not found.
        """
        try:
            start = html.find(base_url)
            if start == -1:
                return None
            
            end = html.find('"', start)
            if end == -1:
                return None
            
            return html[start:end]
        except Exception:
            return None
    
    def _extract_verification_code_from_html(self, html: str) -> Optional[str]:
        """
        Extract verification code from HTML content using regex.
        
        Args:
            html: HTML content to search.
            
        Returns:
            Optional[str]: Extracted verification code or None if not found.
        """
        import re
        
        try:
            match = re.search(r'<td[^>]*>\s*(\d{4})\s*</td>', html)
            return match.group(1) if match else None
        except Exception:
            return None
    
    def _log_email_moved(self, msg: MailMessage, reason: str, success: bool = True) -> None:
        """
        Log details about an email being moved to Gelesen folder.
        
        Args:
            msg: Email message that was moved.
            reason: Reason for moving the email.
            success: Whether the operation was successful.
        """
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
            
            self.notification_handler.log_info(log_message)
            
        except Exception as e:
            self.notification_handler.log_error(f"Error logging email details: {e}")
    
    async def run_email_loop(self) -> None:
        """
        Run the main email checking loop.
        
        This method runs indefinitely, checking for emails at regular intervals.
        """
        check_count = 0
        while True:
            try:
                await self.check_emails()
                
                # Clear processed emails set every 100 checks to prevent memory buildup
                check_count += 1
                if check_count >= 100:
                    self._processed_emails.clear()
                    check_count = 0
                    self.notification_handler.log_debug("🧹 Cleared processed emails cache")
                
                self.notification_handler.log_debug(
                    f"💤 Waiting {self.app_config.check_interval} seconds before next check..."
                )
                await asyncio.sleep(self.app_config.check_interval)
            except EmailProcessingError as e:
                self.notification_handler.log_error(f"❌ Error in email processing: {e}")
                self.notification_handler.log_info("🔄 Reconnecting...")
                await asyncio.sleep(self.app_config.check_interval)
                break  # Break to trigger reconnection
