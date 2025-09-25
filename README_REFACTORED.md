# Netflix VerifyBot - Refactored Version

A modern, well-structured Python application that automatically monitors an email inbox for Netflix verification emails and processes them by clicking verification links and extracting verification codes.

## 🚀 What's New in Version 2.0

This refactored version features a complete architectural overhaul with:

- **Modular Design**: Clean separation of concerns with dedicated modules
- **Type Hints**: Comprehensive type annotations throughout the codebase
- **Better Error Handling**: Custom exception classes and proper error management
- **Improved Testing**: Updated test suite that works with the new architecture
- **Enhanced Documentation**: Detailed docstrings and code comments
- **Configuration Management**: Centralized configuration with validation
- **Async/Await Patterns**: Proper async programming throughout

## 📁 Project Structure

```
netflix-verifybot/
├── __init__.py                 # Package initialization
├── main.py                     # Main entry point
├── app.py                      # Main application class
├── config.py                   # Configuration management
├── email_handler.py            # Email operations and IMAP
├── web_scraper.py              # Web scraping for Netflix links
├── notifications.py            # Logging and Telegram notifications
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── compose.yml                 # Docker Compose configuration
├── netflix-verifybot.service   # Systemd service file
├── config.env.template         # Configuration template
├── README_REFACTORED.md        # This file
└── tests/                      # Test package
    ├── __init__.py
    ├── run_tests.py
    └── test_functionality.py
```

## 🏗️ Architecture

### Core Modules

1. **`config.py`** - Configuration management with validation
2. **`email_handler.py`** - Email operations, IMAP connection, and email processing
3. **`web_scraper.py`** - Web scraping for Netflix verification and confirmation links
4. **`notifications.py`** - Logging and Telegram notification system
5. **`app.py`** - Main application orchestration and lifecycle management

### Key Features

- **Modular Design**: Each module has a single responsibility
- **Type Safety**: Comprehensive type hints for better IDE support and error detection
- **Error Handling**: Custom exception classes for different error types
- **Async Programming**: Proper async/await patterns throughout
- **Configuration Validation**: Automatic validation of configuration settings
- **Resource Management**: Proper cleanup of resources (browser, email connections)
- **Comprehensive Logging**: Structured logging with multiple levels
- **Telegram Integration**: Optional notifications via Telegram

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Docker (for containerized deployment)
- Email account with IMAP access
- (Optional) Telegram bot for notifications

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd netflix-verifybot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application**:
   ```bash
   cp config.env.template config.env
   # Edit config.env with your actual values
   ```

4. **Run tests** (optional but recommended):
   ```bash
   python -m tests.run_tests
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Using Docker Compose** (recommended):
   ```bash
   docker-compose up -d
   ```

2. **Using Docker directly**:
   ```bash
   docker build -t netflix-verifybot .
   docker run -d --name netflix-verifybot netflix-verifybot
   ```

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `config.env.template` to `config.env` and fill in your values:

### Required Settings

- `EMAIL`: Your email address
- `PASSWORD`: Your email password
- `IMAP_SERVER`: Your email provider's IMAP server
- `IMAP_PORT`: IMAP port (usually 993)

### Optional Settings

- `CHECK_INTERVAL`: Email check interval in seconds (default: 3)
- `MINUTES_TO_WAIT`: Wait time before moving old emails (default: 900)
- `MAX_RETRY_ATTEMPTS`: Maximum retry attempts (default: 3)
- `LOG_PATH`: Log file path (default: netflix-validator.log)
- `GELESEN_FOLDER`: Folder name for processed emails (default: Gelesen)

### Telegram Settings (Optional)

- `TELEGRAM_API_KEY`: Your Telegram bot API key
- `TELEGRAM_API_URL`: Your Telegram bot API URL
- `TELEGRAM_CHANNEL_NAME`: Target channel name
- `TELEGRAM_CHANNEL_SECRET`: Channel secret

## 🧪 Testing

The application includes a comprehensive test suite:

```bash
# Run all tests
python -m tests.run_tests

# Run specific test module
python -m tests.test_functionality
```

Tests cover:
- Configuration validation
- Email connection testing
- Telegram configuration validation
- Logging functionality
- Email processing logic

## 📊 Monitoring

### Logs

The application logs to both console and file. Log levels include:
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `DEBUG`: Debug information

### Email Processing

The application automatically:
1. Monitors your inbox for Netflix emails
2. Extracts verification codes from account access emails
3. Clicks verification links in travel verification emails
4. Clicks confirmation links in update location emails
5. Moves processed emails to the "Gelesen" folder

## 🔧 Development

### Code Structure

The refactored code follows these principles:
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Dependencies are injected rather than hardcoded
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Type Safety**: Full type hints for better IDE support
- **Documentation**: Detailed docstrings for all functions and classes

### Adding New Features

1. **New Email Types**: Add processing methods to `EmailHandler`
2. **New Web Scraping**: Extend `WebScraper` class
3. **New Notifications**: Add methods to `NotificationHandler`
4. **Configuration**: Add new settings to `config.py`

### Testing New Features

1. Add tests to `tests/test_functionality.py`
2. Run tests with `python -m tests.run_tests`
3. Ensure all tests pass before deployment

## 🚨 Troubleshooting

### Common Issues

1. **Email Connection Failed**:
   - Check email credentials
   - Verify IMAP server settings
   - Ensure IMAP is enabled on your email account

2. **Telegram Notifications Not Working**:
   - Verify Telegram bot configuration
   - Check API key and channel settings
   - Ensure bot has permission to send messages

3. **Web Scraping Issues**:
   - Check if Playwright is properly installed
   - Verify browser dependencies
   - Check for changes in Netflix's HTML structure

### Debug Mode

Enable debug logging by modifying the log level in the configuration or by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 📈 Performance

The refactored version includes several performance improvements:
- **Resource Management**: Proper cleanup of browser and email connections
- **Async Operations**: Non-blocking email processing and web scraping
- **Error Recovery**: Automatic reconnection with exponential backoff
- **Memory Efficiency**: Better memory management with proper resource cleanup

## 🔒 Security

- **Credential Management**: Use environment variables for sensitive data
- **SSL/TLS**: Secure email connections with SSL/TLS
- **Input Validation**: Proper validation of all inputs
- **Error Handling**: Secure error messages without sensitive information

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on the repository
4. Provide detailed error information and configuration (without sensitive data)

---

**Note**: This refactored version maintains full compatibility with the original functionality while providing a much cleaner, more maintainable codebase. The Docker and environment configurations remain unchanged, ensuring seamless migration from the previous version.
