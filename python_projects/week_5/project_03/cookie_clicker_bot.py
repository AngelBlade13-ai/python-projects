from __future__ import annotations

import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


COOKIE_CLICKER_URL = "https://ozh.github.io/cookieclicker/"
BOT_RUNTIME_SECONDS = 5 * 60
UPGRADE_CHECK_SECONDS = 5


def click_english_if_needed(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Dismiss the language picker on the newer Cookie Clicker page."""
    possible_selectors = [
        "#langSelect-EN",
        '[onclick*="EN"]',
    ]

    for selector in possible_selectors:
        try:
            language_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            language_button.click()
            return
        except TimeoutException:
            continue


def get_cookie_count(driver: webdriver.Chrome) -> int:
    """Read the current cookie count as an integer."""
    cookie_text = driver.find_element(By.ID, "cookies").text
    first_line = cookie_text.splitlines()[0]
    number_text = first_line.split(" cookie")[0]
    number_text = number_text.replace(",", "")

    try:
        return int(float(number_text))
    except ValueError:
        return 0


def buy_best_available_product(driver: webdriver.Chrome) -> None:
    """Buy the most expensive enabled product available in the store."""
    products = driver.find_elements(By.CSS_SELECTOR, "#products .product.enabled")
    if not products:
        return

    # Products are ordered from cheapest to most expensive, so the last enabled
    # product is usually the best one we can currently afford.
    products[-1].click()


def main() -> None:
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(COOKIE_CLICKER_URL)

        click_english_if_needed(driver, wait)

        cookie = wait.until(EC.element_to_be_clickable((By.ID, "bigCookie")))
        timeout = time.time() + BOT_RUNTIME_SECONDS
        next_upgrade_check = time.time() + UPGRADE_CHECK_SECONDS

        while time.time() < timeout:
            cookie.click()

            if time.time() >= next_upgrade_check:
                buy_best_available_product(driver)
                next_upgrade_check = time.time() + UPGRADE_CHECK_SECONDS

        cookies_per_second = driver.find_element(By.ID, "cookiesPerSecond").text
        total_cookies = get_cookie_count(driver)
        print(f"Total cookies: {total_cookies}")
        print(cookies_per_second)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
