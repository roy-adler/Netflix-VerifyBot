# Netflix Autovalidator

This script automatically confirms Netflix location verification emails. It is designed for families who share an account but watch from different households.

1. It logs in to the mailbox specified in `config.env`.
2. It searches for Netflix messages that contain the update-primary-location link, then moves the email to the `Gelesen` folder.
3. Using Playwright, it opens the link and clicks the confirmation button.

Copy `config.env.example` to `config.env` and fill in your mailbox credentials.

This removes the need to manually confirm each viewing session.

**Use responsibly.** Ensure your usage complies with Netflix's terms of service.

## Running with Docker

You can build and run the script as a Docker container:

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

All configuration values are read from environment variables. You can also place them in a `config.env` file and mount it when running the container:

```bash
docker run --env-file config.env netflix-autovalidator
```
