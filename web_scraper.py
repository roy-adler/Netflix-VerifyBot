"""
Web scraping module for Netflix VerifyBot.

This module handles web scraping operations for Netflix verification
and confirmation links.
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Response

from notifications import NotificationHandler


class WebScrapingError(Exception):
    """Raised when there's an error during web scraping operations."""
    pass


class WebScraper:
    """Handles web scraping operations for Netflix links."""
    
    def __init__(self, notification_handler: NotificationHandler):
        """
        Initialize the web scraper.
        
        Args:
            notification_handler: Handler for notifications and logging.
        """
        self.notification_handler = notification_handler
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_browser()
    
    async def _initialize_browser(self) -> None:
        """Initialize the browser instance."""
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
            self._page = await self._browser.new_page()
        except Exception as e:
            raise WebScrapingError(f"Failed to initialize browser: {e}")
    
    async def _close_browser(self) -> None:
        """Close the browser instance."""
        try:
            if self._browser:
                await self._browser.close()
            if hasattr(self, '_playwright'):
                await self._playwright.stop()
        except Exception as e:
            self.notification_handler.log_warning(f"Warning during browser cleanup: {e}")
        finally:
            self._browser = None
            self._page = None
    
    async def click_verification_code_link(self, url: str) -> Optional[str]:
        """
        Click a verification code link and extract the verification code.
        
        Args:
            url: URL of the verification code link.
            
        Returns:
            Optional[str]: Extracted verification code or None if not found.
            
        Raises:
            WebScrapingError: If scraping fails.
        """
        if not self._page:
            raise WebScrapingError("Browser not initialized")
        
        try:
            self.notification_handler.log_info(f"🌍 Opening verification link: {url}")
            
            await self._page.goto(url)
            await self._page.wait_for_selector(
                '[data-uia="travel-verification-otp"]', 
                timeout=5000
            )
            
            verification_code = await self._page.inner_text(
                '[data-uia="travel-verification-otp"]', 
                timeout=5000
            )
            
            if verification_code:
                self.notification_handler.log_info(f"🔢 Verification code: {verification_code}")
                return verification_code
            else:
                self.notification_handler.log_warning("❌ No verification code found")
                return None
                
        except Exception as e:
            raise WebScrapingError(f"Failed to extract verification code: {e}")
    
    async def click_confirmation_link(self, url: str) -> bool:
        """
        Click a confirmation link and verify success.
        
        Args:
            url: URL of the confirmation link.
            
        Returns:
            bool: True if confirmation was successful, False otherwise.
            
        Raises:
            WebScrapingError: If scraping fails.
        """
        if not self._page:
            raise WebScrapingError("Browser not initialized")
        
        try:
            self.notification_handler.log_info(f"🌍 Opening confirmation link: {url}")
            
            await self._page.goto(url)
            await self._page.wait_for_selector(
                '[data-uia="set-primary-location-action"]', 
                timeout=5000
            )
            
            # Wait for a confirmation message or page change to verify success
            response = await self._page.goto(url)
            
            if response and response.status == 200:
                self.notification_handler.log_info("✅ Confirmation link clicked successfully!")
                return True
            else:
                status = response.status if response else 'No response'
                self.notification_handler.log_warning(f"⚠️ Loading error. Status: {status}")
                return False
                
        except Exception as e:
            raise WebScrapingError(f"Failed to click confirmation link: {e}")
    
    async def extract_verification_code_from_page(self, url: str) -> Optional[str]:
        """
        Extract verification code from a Netflix page.
        
        Args:
            url: URL of the page containing the verification code.
            
        Returns:
            Optional[str]: Extracted verification code or None if not found.
        """
        try:
            async with WebScraper(self.notification_handler) as scraper:
                return await scraper.click_verification_code_link(url)
        except WebScrapingError as e:
            self.notification_handler.log_error(f"Failed to extract verification code: {e}")
            return None
    
    async def process_confirmation_link(self, url: str) -> bool:
        """
        Process a confirmation link.
        
        Args:
            url: URL of the confirmation link.
            
        Returns:
            bool: True if confirmation was successful, False otherwise.
        """
        try:
            async with WebScraper(self.notification_handler) as scraper:
                return await scraper.click_confirmation_link(url)
        except WebScrapingError as e:
            self.notification_handler.log_error(f"Failed to process confirmation link: {e}")
            return False


class WebScrapingManager:
    """Manages web scraping operations with proper resource cleanup."""
    
    def __init__(self, notification_handler: NotificationHandler):
        """
        Initialize the web scraping manager.
        
        Args:
            notification_handler: Handler for notifications and logging.
        """
        self.notification_handler = notification_handler
    
    async def process_verification_link(self, url: str) -> Optional[str]:
        """
        Process a verification link and extract the code.
        
        Args:
            url: URL of the verification link.
            
        Returns:
            Optional[str]: Extracted verification code or None if not found.
        """
        try:
            async with WebScraper(self.notification_handler) as scraper:
                return await scraper.click_verification_code_link(url)
        except WebScrapingError as e:
            self.notification_handler.log_error(f"Failed to process verification link: {e}")
            return None
    
    async def process_confirmation_link(self, url: str) -> bool:
        """
        Process a confirmation link.
        
        Args:
            url: URL of the confirmation link.
            
        Returns:
            bool: True if confirmation was successful, False otherwise.
        """
        try:
            async with WebScraper(self.notification_handler) as scraper:
                return await scraper.click_confirmation_link(url)
        except WebScrapingError as e:
            self.notification_handler.log_error(f"Failed to process confirmation link: {e}")
            return False
