from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


WIKIPEDIA_URL = "https://www.wikipedia.org/"


def main() -> None:
    driver = webdriver.Chrome()

    try:
        # Open Wikipedia.
        driver.get(WIKIPEDIA_URL)

        # Find and print the English article count.
        article_count = driver.find_element(By.CSS_SELECTOR, "#articlecount a")
        print(f"English article count: {article_count.text}")

        # Click into the search box, type a search term, and press Enter.
        search_box = driver.find_element(By.NAME, "search")
        search_box.send_keys("Python programming")
        search_box.send_keys(Keys.ENTER)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
