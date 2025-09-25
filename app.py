"""
Main application module for Netflix VerifyBot.

This module contains the main application class and orchestration logic.
"""

import asyncio
import sys
from typing import Optional

from config import Config, ConfigError, load_config, validate_config
from email_handler import EmailHandler, EmailConnectionError, EmailProcessingError
from notifications import NotificationHandler
from web_scraper import WebScrapingManager


class NetflixVerifyBot:
    """Main application class for Netflix VerifyBot."""
    
    def __init__(self, config: Config):
        """
        Initialize the Netflix VerifyBot.
        
        Args:
            config: Application configuration.
        """
        self.config = config
        self.notification_handler = NotificationHandler(
            config.telegram, 
            config.app.log_path
        )
        self.email_handler = EmailHandler(
            config.email,
            config.app,
            self.notification_handler
        )
        self.web_scraper = WebScrapingManager(self.notification_handler)
        self._retry_count = 0
    
    async def start(self) -> None:
        """
        Start the Netflix VerifyBot application.
        
        This method runs the main application loop with proper error handling
        and retry logic.
        """
        try:
            # Test configuration
            await self._test_configuration()
            
            # Show startup information
            self._show_startup_info()
            
            # Run the main application loop
            await self._run_main_loop()
            
        except KeyboardInterrupt:
            self.notification_handler.log_info("🛑 Application stopped by user")
        except Exception as e:
            self.notification_handler.log_error(f"💀 Fatal error: {e}")
            sys.exit(1)
        finally:
            await self._cleanup()
    
    async def _test_configuration(self) -> None:
        """
        Test the application configuration before starting.
        
        Raises:
            ConfigError: If configuration is invalid.
        """
        self.notification_handler.log_info("Testing application configuration...")
        
        try:
            validate_config(self.config)
            self.notification_handler.log_info("✅ Configuration validation successful")
        except ConfigError as e:
            self.notification_handler.log_error(f"❌ Configuration error: {e}")
            raise
    
    def _show_startup_info(self) -> None:
        """Display startup information."""
        self.notification_handler.log_info(
            f"🔄 Starting Netflix Autovalidator - checking every {self.config.app.check_interval} seconds"
        )
        
        telegram_status = self.notification_handler.get_telegram_status()
        self.notification_handler.log_info(
            f"📝 Logging to {self.config.app.log_path} and Telegram notifications {telegram_status}"
        )
    
    async def _run_main_loop(self) -> None:
        """Run the main application loop with retry logic."""
        while self._retry_count < self.config.app.max_retry_attempts:
            try:
                await self._run_email_loop()
                # If we reach here, connection was successful, reset retry count
                self._retry_count = 0
                
            except (EmailConnectionError, EmailProcessingError) as e:
                self._retry_count += 1
                self.notification_handler.log_error(
                    f"❌ Failed to connect (attempt {self._retry_count}/{self.config.app.max_retry_attempts}): {e}"
                )
                
                if self._retry_count >= self.config.app.max_retry_attempts:
                    self.notification_handler.log_error(
                        f"💀 Maximum retry attempts ({self.config.app.max_retry_attempts}) reached. Shutting down gracefully."
                    )
                    self.notification_handler.log_error(
                        "🛑 Netflix VerifyBot is stopping to prevent infinite loops and spam."
                    )
                    sys.exit(0)  # Exit with code 0 for graceful shutdown
                else:
                    # Use exponential backoff: wait longer between retries
                    wait_time = self.config.app.check_interval * (2 ** (self._retry_count - 1))
                    self.notification_handler.log_info(f"🔄 Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
    
    async def _run_email_loop(self) -> None:
        """Run the email processing loop."""
        try:
            await self.email_handler.connect()
            await self.email_handler.run_email_loop()
        finally:
            await self.email_handler.disconnect()
    
    async def _cleanup(self) -> None:
        """Cleanup resources before shutdown."""
        try:
            await self.email_handler.disconnect()
            self.notification_handler.log_info("👋 Netflix VerifyBot has stopped")
        except Exception as e:
            self.notification_handler.log_warning(f"Warning during cleanup: {e}")


async def main():
    """Main entry point for the application."""
    try:
        # Load and validate configuration
        config = load_config()
        
        # Create and start the application
        app = NetflixVerifyBot(config)
        await app.start()
        
    except ConfigError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
