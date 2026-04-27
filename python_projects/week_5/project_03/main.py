from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.common.by import By


PYTHON_HOME_URL = "https://www.python.org/"


def main() -> None:
    # Selenium Manager will find/download the matching ChromeDriver automatically.
    driver = webdriver.Chrome()

    try:
        # Open the Python home page.
        driver.get(PYTHON_HOME_URL)

        # Find the upcoming event dates and names with CSS selectors.
        event_times = driver.find_elements(By.CSS_SELECTOR, ".event-widget time")
        event_names = driver.find_elements(By.CSS_SELECTOR, ".event-widget li a")

        # Build the dictionary format from the lesson.
        events: dict[int, dict[str, str]] = {}
        for index in range(len(event_times)):
            events[index] = {
                "time": event_times[index].text,
                "name": event_names[index].text,
            }

        print(events)
    finally:
        # Always close the browser when the script is done.
        driver.quit()


if __name__ == "__main__":
    main()
