# Project 03: Selenium Browser Automation

This project follows the safe Day 48 Selenium path: browser setup, element location, page interaction, and a small Cookie Clicker automation exercise.


## Setup

1. Install Google Chrome.
2. Open a terminal in this folder.
3. Install Selenium:

```bash
pip install -r requirements.txt
```

Modern Selenium includes Selenium Manager, which can automatically locate or download the correct ChromeDriver for your installed Chrome version.

## Files

- `main.py`: opens `python.org`, finds upcoming event times and names, and prints the event dictionary from the lesson.
- `interaction.py`: opens Wikipedia, prints the English article count, types a search term, and presses Enter.
- `cookie_clicker_bot.py`: opens the Cookie Clicker GitHub Pages game, clicks the cookie, buys the best available product every 5 seconds, and prints cookies per second after 5 minutes.

## Run

```bash
python main.py
python interaction.py
python cookie_clicker_bot.py
```

Run one file at a time.

## Notes

- Selenium opens a real Chrome browser controlled by Python.
- `driver.quit()` closes the browser when each script finishes.
- If ChromeDriver setup fails, update Chrome and Selenium, then rerun the script.
- The Cookie Clicker bot is for a harmless practice game only.
