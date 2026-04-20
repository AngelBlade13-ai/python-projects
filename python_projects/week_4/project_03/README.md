# Project 03: Exercise Tracker

This project logs natural-language exercise entries using the Nutritionix exercise API and sends the parsed workout data to a Google Sheet through Sheety.

## Files to Submit

Submit this folder with:

- `main.py`
- `.env.example`
- `README.md`

Do not submit your real `.env` file or any live API credentials.

## Setup

1. Make a copy of this Google Sheet:
   - https://docs.google.com/spreadsheets/d/1DHL6Y8XAHSC_KhJsa9QMekwP8b4YheWZY_sxlH3i494/edit?usp=sharing
2. Create a free account and API credentials here:
   - https://app.100daysofpython.dev/
3. Create a Sheety project connected to your copied spreadsheet and enable your preferred authentication method.
4. Copy `.env.example` to `.env`.
5. Fill in these values in `.env`:
   - `APP_ID`
   - `API_KEY`
   - `SHEET_ENDPOINT`
   - `TOKEN`
6. Optionally fill in:
   - `USERNAME`
   - `PASSWORD`
   - `GENDER`
   - `WEIGHT_KG`
   - `HEIGHT_CM`
   - `AGE`

If `GENDER`, `WEIGHT_KG`, `HEIGHT_CM`, or `AGE` are left blank, the program will prompt for them when it runs.

## Run

From this folder, run:

```bash
python main.py
```

Then enter a sentence such as:

```text
Running for 30 minutes and cycling for 20 minutes
```

## What It Does

- Sends the exercise text to Nutritionix
- Parses the returned exercise name, duration, and calories
- Adds the current date and time
- Posts each workout row to the Sheety endpoint

## Notes

- This version uses Python standard library HTTP support, so it does not require `requests`.
- Bearer tokens with spaces may fail in Sheety. A token without spaces is safer.
