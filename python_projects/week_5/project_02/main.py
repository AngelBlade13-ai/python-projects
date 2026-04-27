from __future__ import annotations

import os
import re
import smtplib
from email.message import EmailMessage
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PRACTICE_PAGE_URL = "https://appbrewery.github.io/instant_pot/"
TARGET_PRICE = 100.00


def load_dotenv() -> None:
    """Load simple KEY=VALUE pairs from a local .env file."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not os.getenv(key):
            os.environ[key] = value


def get_required_env(variable_name: str) -> str:
    """Read one required environment variable or raise a helpful error."""
    value = os.getenv(variable_name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {variable_name}")
    return value


def parse_price(price_text: str) -> float:
    """Convert a price string like '$99.99' into a float like 99.99."""
    cleaned_price = price_text.strip().replace("$", "").replace(",", "")
    try:
        return float(cleaned_price)
    except ValueError as error:
        raise ValueError(f"Could not convert price to a number: {price_text!r}") from error


def clean_text(text: str) -> str:
    """Replace repeated spaces and line breaks with a single space."""
    return re.sub(r"\s+", " ", text).strip()


def get_product_data() -> tuple[str, float]:
    """Request the practice page and return the product title and price."""
    # Step 1: Fetch the static practice page.
    response = requests.get(PRACTICE_PAGE_URL, timeout=30)
    response.raise_for_status()

    # Step 2: Parse the HTML with BeautifulSoup.
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 3: Find the title and price elements on the page.
    title_element = soup.select_one("#productTitle")
    if title_element is None:
        raise RuntimeError("Could not find the product title on the practice page.")

    price_element = soup.select_one(".a-price .a-offscreen")
    if price_element is None:
        raise RuntimeError("Could not find the product price on the practice page.")

    # Step 4: Convert the scraped text into clean Python values.
    product_title = clean_text(title_element.get_text(" ", strip=True))
    product_price = parse_price(price_element.get_text(strip=True))
    return product_title, product_price


def send_price_alert(product_title: str, product_price: float) -> None:
    """Send a test email to yourself when the product is below the target price."""
    smtp_address = get_required_env("SMTP_ADDRESS")
    smtp_port = int(get_required_env("SMTP_PORT"))
    email_address = get_required_env("EMAIL_ADDRESS")
    email_password = get_required_env("EMAIL_PASSWORD")
    to_email = get_required_env("TO_EMAIL")

    # Build a plain text email message.
    email = EmailMessage()
    email["Subject"] = f"Practice Page Price Alert! ${product_price:.2f}"
    email["From"] = email_address
    email["To"] = to_email
    email.set_content(
        f"{product_title}\n\n"
        f"Current price: ${product_price:.2f}\n"
        f"Target price: ${TARGET_PRICE:.2f}\n\n"
        f"Practice page: {PRACTICE_PAGE_URL}"
    )

    # Connect to the SMTP server and send the test email.
    with smtplib.SMTP(smtp_address, smtp_port) as connection:
        connection.starttls()
        connection.login(email_address, email_password)
        connection.send_message(email)


def main() -> None:
    # Load email settings from .env before reading environment variables.
    load_dotenv()

    try:
        product_title, product_price = get_product_data()
    except requests.HTTPError as error:
        print(f"Request failed with an HTTP error: {error}")
        return
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return
    except Exception as error:
        print(f"Could not read product data: {error}")
        return

    print(f"Product title: {product_title}")
    print(f"Current price: ${product_price:.2f}")
    print(f"Target price: ${TARGET_PRICE:.2f}")

    # Only send an email if the current price is below the target price.
    if product_price >= TARGET_PRICE:
        print("The price is not below the target, so no email was sent.")
        return

    try:
        send_price_alert(product_title, product_price)
    except Exception as error:
        print(f"The price is below target, but the email could not be sent: {error}")
        return

    print("The price is below target. Test email sent.")


if __name__ == "__main__":
    main()
