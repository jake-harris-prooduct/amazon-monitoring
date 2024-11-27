# Amazon Book Monitor

A Python script to monitor Amazon book listings for:
- Stock availability
- Kindle availability
- Review scores
- Sends email alerts when issues are detected

## Setup

1. Clone this repository
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `config.json` file based on the template
4. Update the config with your:
   - Book URLs
   - Email settings
   - Notification preferences

## Configuration

Create a `config.json` file with the following structure:

```json
{
    "book_urls": [
        "https://www.amazon.com/your-book-url-1",
        "https://www.amazon.com/your-book-url-2"
    ],
    "min_review_score": 4.0,
    "send_daily_report": true,
    "email_recipients": ["your@email.com", "colleague@email.com"],
    "smtp": {
        "server": "smtp.gmail.com",
        "port": 587,
        "email": "your-sending-email@gmail.com",
        "password": "your-app-specific-password"
    }
}
```

## Usage

Run the script manually:
```bash
python monitor.py
```

Or set up as a scheduled task on PythonAnywhere.
