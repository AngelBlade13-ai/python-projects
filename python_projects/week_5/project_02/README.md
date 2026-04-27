# Project 02: Practice Price Alert

This beginner project reads the static App Brewery practice page, extracts the product title and price, and sends a test email when the price is below `TARGET_PRICE`.

Practice page:

```text
https://appbrewery.github.io/instant_pot/
```

This project intentionally uses only the static practice page and does not scrape live commercial sites.

## Why This Differs From The Lesson

The original lesson plan starts with the App Brewery practice page and then moves on to scraping a real Amazon product page. This project stops at the practice page on purpose.

Live commercial product pages change often and may include bot detection, CAPTCHA pages, regional page differences, authentication requirements, rate limits, robots.txt rules, and Terms of Service restrictions. A beginner project should focus on the Python skills being practiced, not on trying to work around those protections.

This version keeps the useful learning goals:

- request a page with `requests`
- parse HTML with `BeautifulSoup`
- extract a product title and price
- convert the price to a `float`
- compare it against `TARGET_PRICE`
- send a personal test email with `smtplib`
- keep email credentials in `.env`

The live-site scraping portion was intentionally removed. The email subject also says `Practice Page Price Alert!` instead of an Amazon-specific alert because this script only tracks the static practice page.

## Setup

1. Open a terminal in this folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Fill in your email settings:

```text
SMTP_ADDRESS="smtp.gmail.com"
SMTP_PORT="587"
EMAIL_ADDRESS="your_email@example.com"
EMAIL_PASSWORD="your_email_app_password"
TO_EMAIL="your_email@example.com"
```

Use an app password from your email provider when required. Do not use your normal account password.

For Gmail, this is required. If you see an error like `Application-specific password required`, turn on 2-Step Verification for your Google account, create a Gmail app password, and use that app password as `EMAIL_PASSWORD`.

## Run

```bash
python main.py
```

The script prints the product title, current price, and target price. If the practice-page price is below `100.00`, it sends a test email to `TO_EMAIL`.

## Notes

- The target price is set in `main.py` as `TARGET_PRICE = 100.00`.
- The script uses `requests` and `BeautifulSoup` only on the static practice page.
- Email credentials are read from environment variables or `.env`; they are not hard-coded.
- `.env` is ignored by git because it can contain private credentials.
