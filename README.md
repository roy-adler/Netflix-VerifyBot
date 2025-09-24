# Netflix Autovalidator

This script automatically confirms Netflix location verification emails. It is designed for families who share an account but watch from different households.

## Features

- Automatically processes Netflix location verification emails
- Moves processed emails to "Gelesen" folder for organization
- Sends Telegram notifications about processing status
- Comprehensive logging with configurable log paths
- Auto-cleanup of old read emails (15+ minutes)
- Docker and Docker Compose support

## How It Works

1. It logs in to the mailbox specified in `config.env`.
2. It searches for Netflix messages that contain the update-primary-location link, then moves the email to the `Gelesen` folder.
3. Using Playwright, it opens the link and clicks the confirmation button.
4. Sends notifications to configured Telegram channels.
5. Automatically moves old read emails to keep inbox clean.

This removes the need to manually confirm each viewing session.

**Use responsibly.** Ensure your usage complies with Netflix's terms of service.

## Configuration

Copy `config.env.example` to `config.env` and configure:

### Required
- `EMAIL`: Your email address
- `PASSWORD`: Your email password  
- `IMAP_SERVER`: Your IMAP server address
- `IMAP_PORT`: IMAP port (usually 993)

### Optional
- `LOG_PATH`: Log file path (default: "netflix-validator.log")
- `TELEGRAM_API_KEY`: API key for notifications
- `TELEGRAM_API_URL`: Telegram bot API URL
- `TELEGRAM_CHANNEL_NAME`: Channel name
- `TELEGRAM_CHANNEL_SECRET`: Channel secret

## Running with Docker

### Docker Run
```bash
# build the image
docker build -t netflix-autovalidator .

# run the container
docker run -e EMAIL=you@example.com \
           -e PASSWORD=yourpassword \
           -e IMAP_SERVER=imap.example.com \
           -e IMAP_PORT=993 \
           netflix-autovalidator
```

Or with config file:
```bash
docker run --env-file config.env netflix-autovalidator
```

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

## Local Installation

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```
