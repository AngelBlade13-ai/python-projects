import os
import json
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


EXERCISE_ENDPOINT = "https://app.100daysofpython.dev/v1/nutrition/natural/exercise"


def load_dotenv():
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


def get_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_profile_value(env_name, prompt_text, cast_func=str):
    value = os.getenv(env_name)
    if value:
        return cast_func(value)
    return cast_func(input(prompt_text).strip())


def get_gender():
    gender = get_profile_value("GENDER", "Gender: ", str).strip().lower()
    if gender not in {"male", "female"}:
        raise RuntimeError('GENDER must be "male" or "female".')
    return gender


def post_json(url, payload, headers=None):
    request = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    request.add_header("Content-Type", "application/json")
    if headers:
        for key, value in headers.items():
            request.add_header(key, value)

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code} error from {url}: {message}") from error
    except URLError as error:
        raise RuntimeError(f"Request failed for {url}: {error.reason}") from error


def build_sheet_headers():
    token = os.getenv("TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def build_sheet_auth():
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    if username and password:
        return username, password
    return None


def get_exercise_data(exercise_text, profile):
    headers = {
        "x-app-id": get_env("APP_ID"),
        "x-app-key": get_env("API_KEY"),
    }
    payload = {
        "query": exercise_text,
        "gender": profile["gender"],
        "weight_kg": profile["weight_kg"],
        "height_cm": profile["height_cm"],
        "age": profile["age"],
    }
    return post_json(EXERCISE_ENDPOINT, payload, headers=headers)


def log_workout(sheet_endpoint, workout_row, headers, auth):
    request_headers = dict(headers)
    if auth:
        username, password = auth
        token = f"{username}:{password}".encode("utf-8")
        import base64
        request_headers["Authorization"] = f"Basic {base64.b64encode(token).decode('ascii')}"

    return post_json(sheet_endpoint, {"workout": workout_row}, headers=request_headers)


def main():
    profile = {
        "gender": get_gender(),
        "weight_kg": get_profile_value("WEIGHT_KG", "Weight (kg): ", float),
        "height_cm": get_profile_value("HEIGHT_CM", "Height (cm): ", float),
        "age": get_profile_value("AGE", "Age: ", int),
    }
    sheet_endpoint = get_env("SHEET_ENDPOINT")
    sheet_headers = build_sheet_headers()
    sheet_auth = build_sheet_auth()

    exercise_text = input("Tell me which exercises you did: ").strip()
    if not exercise_text:
        raise RuntimeError("Exercise input cannot be empty.")

    result = get_exercise_data(exercise_text, profile)

    now = datetime.now()
    today_date = now.strftime("%d/%m/%Y")
    now_time = now.strftime("%X")

    for exercise in result["exercises"]:
        workout_row = {
            "date": today_date,
            "time": now_time,
            "exercise": exercise["name"].title(),
            "duration": exercise["duration_min"],
            "calories": exercise["nf_calories"],
        }
        logged_row = log_workout(sheet_endpoint, workout_row, sheet_headers, sheet_auth)
        print(logged_row)


if __name__ == "__main__":
    load_dotenv()
    main()
