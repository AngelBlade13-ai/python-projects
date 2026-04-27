from __future__ import annotations

import os
import json
import re
import time
from datetime import date, datetime, timedelta
from html import unescape
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

try:
    from ytmusicapi import OAuthCredentials, YTMusic
    from ytmusicapi.auth.oauth.token import RefreshingToken, Token
except ImportError:
    OAuthCredentials = None
    RefreshingToken = None
    Token = None
    YTMusic = None


CHART_URL_TEMPLATE = "https://appbrewery.github.io/bakeboard-hot-100/{date}/"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    )
}
BROWSER_AUTH_FILE = "browser.json"
OAUTH_AUTH_FILE = "oauth.json"
PLAYLIST_CACHE_FILE = "playlist_cache.json"
SONG_CACHE_FILE = "song_cache.json"
MAX_FALLBACK_WEEKS = 52
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
ytmusic_search_fallback_announced = False


class YouTubeApiError(RuntimeError):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"YouTube Data API returned HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message


class YouTubeQuotaExceededError(YouTubeApiError):
    pass


def load_dotenv() -> None:
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


def prompt_for_date() -> date:
    date_text = input(
        "Which year do you want to travel to? Type a date in this format "
        "YYYY-MM-DD (example: 2000-08-12): "
    ).strip().encode("ascii", "ignore").decode()

    try:
        parsed_date = datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("Date must be in YYYY-MM-DD format.") from error

    if parsed_date.date() > datetime.today().date():
        raise ValueError("Date cannot be in the future.")

    return parsed_date.date()


def format_chart_date(chart_date: date) -> str:
    return chart_date.isoformat()


def nearest_saturday(target_date: date, direction: int) -> date:
    saturday_index = 5
    days_until_saturday = (saturday_index - target_date.weekday()) % 7
    next_saturday = target_date + timedelta(days=days_until_saturday)
    if direction >= 0:
        return next_saturday

    days_since_saturday = (target_date.weekday() - saturday_index) % 7
    return target_date - timedelta(days=days_since_saturday)


def build_fallback_candidates(target_date: date) -> list[date]:
    seen: set[date] = set()
    candidates: list[date] = [target_date]

    previous_saturday = nearest_saturday(target_date, direction=-1)
    next_saturday = nearest_saturday(target_date, direction=1)
    candidates.extend([previous_saturday, next_saturday])

    for week_offset in range(1, MAX_FALLBACK_WEEKS + 1):
        delta = timedelta(days=7 * week_offset)
        candidates.append(previous_saturday - delta)
        candidates.append(next_saturday + delta)

    unique_candidates: list[date] = []
    for candidate in candidates:
        if candidate > datetime.today().date() or candidate in seen:
            continue
        seen.add(candidate)
        unique_candidates.append(candidate)
    return unique_candidates


def fetch_chart_page(chart_date: date) -> requests.Response:
    chart_url = CHART_URL_TEMPLATE.format(date=format_chart_date(chart_date))
    response = requests.get(chart_url, headers=REQUEST_HEADERS, timeout=30)
    return response


def scrape_chart_entries(chart_date: date) -> list[dict[str, str]]:
    response = fetch_chart_page(chart_date)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title_elements = soup.select("h3.chart-entry__title")
    artist_elements = soup.select("span.chart-entry__artist")

    if not title_elements or not artist_elements:
        raise RuntimeError(
            f"Could not find chart entries on {response.url}."
        )

    if len(title_elements) != len(artist_elements):
        raise RuntimeError(
            "The scraped chart data is incomplete because the title and artist "
            "counts do not match."
        )

    entries: list[dict[str, str]] = []
    for title_element, artist_element in zip(title_elements, artist_elements, strict=True):
        title = unescape(title_element.get_text(strip=True))
        artist = unescape(artist_element.get_text(strip=True))
        entries.append({"title": title, "artist": artist})

    return entries


def resolve_chart_date(target_date: date) -> tuple[date, list[dict[str, str]]]:
    attempted_dates: list[date] = []

    for candidate in build_fallback_candidates(target_date):
        attempted_dates.append(candidate)
        response = fetch_chart_page(candidate)

        if response.status_code == 404:
            continue
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title_elements = soup.select("h3.chart-entry__title")
        artist_elements = soup.select("span.chart-entry__artist")
        if not title_elements or not artist_elements:
            continue

        entries: list[dict[str, str]] = []
        for title_element, artist_element in zip(title_elements, artist_elements, strict=True):
            entries.append(
                {
                    "title": unescape(title_element.get_text(strip=True)),
                    "artist": unescape(artist_element.get_text(strip=True)),
                }
            )
        return candidate, entries

    attempted_preview = ", ".join(format_chart_date(item) for item in attempted_dates[:10])
    raise RuntimeError(
        "No chart data was found near that date. "
        f"Dates checked started with: {attempted_preview}"
    )


def print_chart_entries(entries: list[dict[str, str]]) -> None:
    print("\nTop 100 songs:\n")
    for index, entry in enumerate(entries, start=1):
        print(f"{index:>3}. {entry['title']} - {entry['artist']}")


def load_playlist_cache(project_dir: Path) -> dict[str, str]:
    cache_path = project_dir / PLAYLIST_CACHE_FILE
    if not cache_path.exists():
        return {}

    try:
        raw_cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(raw_cache, dict):
        return {}

    return {
        str(title): str(playlist_id)
        for title, playlist_id in raw_cache.items()
        if title and playlist_id
    }


def save_playlist_cache(project_dir: Path, cache: dict[str, str]) -> None:
    cache_path = project_dir / PLAYLIST_CACHE_FILE
    cache_path.write_text(
        json.dumps(cache, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def get_cached_playlist_id(project_dir: Path, playlist_title: str) -> str | None:
    return load_playlist_cache(project_dir).get(playlist_title)


def remember_playlist_id(project_dir: Path, playlist_title: str, playlist_id: str) -> None:
    cache = load_playlist_cache(project_dir)
    cache[playlist_title] = playlist_id
    save_playlist_cache(project_dir, cache)


def song_cache_key(title: str, artist: str) -> str:
    return f"{clean_search_text(title).casefold()}::{clean_search_text(artist).casefold()}"


def load_song_cache(project_dir: Path) -> dict[str, str]:
    cache_path = project_dir / SONG_CACHE_FILE
    if not cache_path.exists():
        return {}

    try:
        raw_cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(raw_cache, dict):
        return {}

    return {
        str(song_key): str(video_id)
        for song_key, video_id in raw_cache.items()
        if song_key and video_id
    }


def save_song_cache(project_dir: Path, cache: dict[str, str]) -> None:
    cache_path = project_dir / SONG_CACHE_FILE
    cache_path.write_text(
        json.dumps(cache, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def get_youtube_access_token(project_dir: Path) -> str | None:
    if OAuthCredentials is None or RefreshingToken is None or Token is None:
        return None

    token_path = project_dir / OAUTH_AUTH_FILE
    if not token_path.exists():
        return None

    client_id = os.getenv("YTMUSIC_CLIENT_ID")
    client_secret = os.getenv("YTMUSIC_CLIENT_SECRET")
    if not client_id or not client_secret:
        return None

    try:
        token_data = json.loads(token_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    token_fields = set(Token.members())
    filtered_token = {
        key: value
        for key, value in token_data.items()
        if key in token_fields
    }
    credentials = OAuthCredentials(client_id=client_id, client_secret=client_secret)
    token = RefreshingToken(credentials=credentials, **filtered_token)
    token._local_cache = token_path
    return token.access_token


def youtube_api_request(
    project_dir: Path,
    method: str,
    endpoint: str,
    params: dict[str, str | int] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    access_token = get_youtube_access_token(project_dir)
    if not access_token:
        raise RuntimeError("No OAuth access token is available for the YouTube Data API.")

    response = requests.request(
        method=method,
        url=f"{YOUTUBE_API_BASE_URL}/{endpoint}",
        params=params,
        json=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        timeout=30,
    )

    if response.status_code >= 400:
        try:
            error_data = response.json()
            message = error_data.get("error", {}).get("message", response.text)
        except ValueError:
            message = response.text
        if response.status_code == 403 and "quota" in message.casefold():
            raise YouTubeQuotaExceededError(response.status_code, message)
        raise YouTubeApiError(response.status_code, message)

    if not response.text:
        return {}
    return response.json()


def get_youtube_playlist_video_ids(project_dir: Path, playlist_id: str) -> set[str]:
    video_ids: set[str] = set()
    page_token: str | None = None

    while True:
        params: dict[str, str | int] = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token

        response = youtube_api_request(
            project_dir,
            "GET",
            "playlistItems",
            params=params,
        )

        for item in response.get("items", []):
            video_id = (
                item.get("snippet", {})
                .get("resourceId", {})
                .get("videoId")
            )
            if video_id:
                video_ids.add(video_id)

        page_token = response.get("nextPageToken")
        if not page_token:
            return video_ids


def create_youtube_playlist(project_dir: Path, playlist_title: str) -> str:
    response = youtube_api_request(
        project_dir,
        "POST",
        "playlists",
        params={"part": "snippet,status"},
        body={
            "snippet": {
                "title": playlist_title,
                "description": (
                    "Top 100 songs from the Billboard chart for "
                    f"{playlist_title[:10]}."
                ),
            },
            "status": {"privacyStatus": "private"},
        },
    )

    playlist_id = response.get("id")
    if not playlist_id:
        raise RuntimeError(f"Could not determine playlist id from response: {response}")
    return playlist_id


def add_youtube_playlist_item(project_dir: Path, playlist_id: str, video_id: str) -> None:
    for attempt in range(1, 4):
        try:
            youtube_api_request(
                project_dir,
                "POST",
                "playlistItems",
                params={"part": "snippet"},
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id,
                        },
                    },
                },
            )
            return
        except YouTubeApiError as error:
            if error.status_code != 409 or attempt == 3:
                raise
            time.sleep(attempt * 2)


def clean_search_text(value: str) -> str:
    value = re.sub(r"\b(featuring|feat\.?|with)\b", " ", value, flags=re.IGNORECASE)
    value = value.replace("&", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def search_youtube_video_id(project_dir: Path, title: str, artist: str) -> str | None:
    query = f"{clean_search_text(title)} {clean_search_text(artist)} official audio"
    response = youtube_api_request(
        project_dir,
        "GET",
        "search",
        params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "10",
            "maxResults": 5,
        },
    )

    for item in response.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            return video_id

    return None


def get_existing_playlist_from_cache(
    yt: YTMusic,
    project_dir: Path,
    playlist_title: str,
) -> tuple[str, set[str]] | None:
    playlist_id = get_cached_playlist_id(project_dir, playlist_title)
    if not playlist_id:
        return None

    try:
        existing_video_ids = get_existing_video_ids(yt, playlist_id)
    except Exception as error:
        print(f"Could not read cached playlist with YouTube Music ({error}).")
        try:
            existing_video_ids = get_youtube_playlist_video_ids(project_dir, playlist_id)
        except YouTubeQuotaExceededError:
            raise
        except Exception as api_error:
            print(
                "Cached playlist could not be loaded, so a new playlist will be created "
                f"({api_error})."
            )
            return None

    return playlist_id, existing_video_ids


def get_existing_playlist_id(yt: YTMusic, playlist_title: str) -> str | None:
    try:
        playlists = yt.get_library_playlists(limit=100)
    except Exception as error:
        print(
            "Could not read your YouTube Music library, so the local playlist cache "
            f"will be used instead ({error})."
        )
        return None

    for playlist in playlists:
        if playlist.get("title") == playlist_title:
            return playlist.get("playlistId")
    return None


def get_existing_video_ids(yt: YTMusic, playlist_id: str) -> set[str]:
    playlist = yt.get_playlist(playlist_id, limit=500)
    tracks = playlist.get("tracks", [])
    return {
        track["videoId"]
        for track in tracks
        if isinstance(track, dict) and track.get("videoId")
    }


def create_or_reuse_playlist(
    yt: YTMusic,
    project_dir: Path,
    playlist_title: str,
) -> tuple[str, set[str], bool]:
    cached_playlist = get_existing_playlist_from_cache(yt, project_dir, playlist_title)
    if cached_playlist:
        playlist_id, existing_video_ids = cached_playlist
        return playlist_id, existing_video_ids, False

    existing_playlist_id = get_existing_playlist_id(yt, playlist_title)
    if existing_playlist_id:
        existing_video_ids = get_existing_video_ids(yt, existing_playlist_id)
        remember_playlist_id(project_dir, playlist_title, existing_playlist_id)
        return existing_playlist_id, existing_video_ids, False

    try:
        creation_result = yt.create_playlist(
            title=playlist_title,
            description=f"Top 100 songs from the Billboard chart for {playlist_title[:10]}.",
            privacy_status="PRIVATE",
        )
        playlist_id = extract_playlist_id(creation_result)
    except Exception as error:
        print(
            "Could not create the playlist with YouTube Music, so the YouTube Data "
            f"API will be used instead ({error})."
        )
        playlist_id = create_youtube_playlist(project_dir, playlist_title)

    remember_playlist_id(project_dir, playlist_title, playlist_id)
    return playlist_id, set(), True


def extract_playlist_id(result: str | dict[str, Any]) -> str:
    if isinstance(result, str):
        return result

    playlist_id = result.get("playlistId") or result.get("id")
    if not playlist_id:
        raise RuntimeError(f"Could not determine playlist id from response: {result}")
    return playlist_id


def search_song_video_id(
    yt: YTMusic,
    project_dir: Path,
    song_cache: dict[str, str],
    title: str,
    artist: str,
) -> str | None:
    global ytmusic_search_fallback_announced
    cache_key = song_cache_key(title, artist)
    if cache_key in song_cache:
        return song_cache[cache_key]

    try:
        results = yt.search(f"{title} {artist}", filter="songs", limit=5)
    except Exception as error:
        if not ytmusic_search_fallback_announced:
            print(
                "YouTube Music search failed, so YouTube Data API search will be "
                f"used for song lookups ({error})."
            )
            ytmusic_search_fallback_announced = True
        video_id = search_youtube_video_id(project_dir, title, artist)
        if video_id:
            song_cache[cache_key] = video_id
            save_song_cache(project_dir, song_cache)
        return video_id

    expected_artist = artist.casefold()
    for result in results:
        artist_names = " ".join(
            artist_item.get("name", "")
            for artist_item in result.get("artists", [])
            if isinstance(artist_item, dict)
        ).casefold()
        video_id = result.get("videoId")
        if video_id and expected_artist and expected_artist in artist_names:
            song_cache[cache_key] = video_id
            save_song_cache(project_dir, song_cache)
            return video_id

    for result in results:
        video_id = result.get("videoId")
        if video_id:
            song_cache[cache_key] = video_id
            save_song_cache(project_dir, song_cache)
            return video_id

    video_id = search_youtube_video_id(project_dir, title, artist)
    if video_id:
        song_cache[cache_key] = video_id
        save_song_cache(project_dir, song_cache)
    return video_id


def add_songs_to_playlist(
    yt: YTMusic,
    project_dir: Path,
    playlist_id: str,
    entries: list[dict[str, str]],
    existing_video_ids: set[str],
) -> tuple[int, int, int]:
    added_count = 0
    skipped_duplicates = 0
    failed_count = 0
    song_cache = load_song_cache(project_dir)

    for entry in entries:
        title = entry["title"]
        artist = entry["artist"]

        try:
            video_id = search_song_video_id(yt, project_dir, song_cache, title, artist)
            if not video_id:
                failed_count += 1
                print(f"Skipped: no result found for {title} - {artist}")
                continue

            if video_id in existing_video_ids:
                skipped_duplicates += 1
                print(f"Skipped: already in playlist: {title} - {artist}")
                continue

            try:
                yt.add_playlist_items(playlist_id, [video_id])
            except Exception:
                add_youtube_playlist_item(project_dir, playlist_id, video_id)

            existing_video_ids.add(video_id)
            added_count += 1
            print(f"Added: {title} - {artist}")
        except YouTubeQuotaExceededError as error:
            failed_count += 1
            print(f"Stopped: YouTube API quota is exhausted while processing {title} - {artist}.")
            print(f"Quota message: {error.message}")
            print("Run the script again after the daily quota resets; cached searches will be reused.")
            break
        except Exception as error:
            failed_count += 1
            print(f"Skipped: {title} - {artist} ({error})")

    return added_count, skipped_duplicates, failed_count


def create_authenticated_ytmusic(project_dir: Path) -> YTMusic | None:
    if YTMusic is None:
        print(
            "\nThe scrape step completed, but ytmusicapi is not installed so the "
            "playlist step was skipped."
        )
        print("Install it with 'pip install -r requirements.txt' and run the script again.")
        return None

    oauth_auth_path = project_dir / OAUTH_AUTH_FILE
    if oauth_auth_path.exists():
        client_id = os.getenv("YTMUSIC_CLIENT_ID")
        client_secret = os.getenv("YTMUSIC_CLIENT_SECRET")
        if not client_id or not client_secret:
            print(
                "\nFound oauth.json, but YTMUSIC_CLIENT_ID and "
                "YTMUSIC_CLIENT_SECRET are missing."
            )
            print(
                "Add them to your environment or a local .env file, then run the script again."
            )
            return None

        return YTMusic(
            str(oauth_auth_path),
            oauth_credentials=OAuthCredentials(
                client_id=client_id,
                client_secret=client_secret,
            ),
        )

    browser_auth_path = project_dir / BROWSER_AUTH_FILE
    if browser_auth_path.exists():
        return YTMusic(str(browser_auth_path))

    print(
        "\nScraping completed. No YouTube Music auth file was found, so the playlist "
        "step was skipped."
    )
    print(
        "Preferred setup: create oauth.json with 'python setup_oauth.py' and set "
        "YTMUSIC_CLIENT_ID / YTMUSIC_CLIENT_SECRET."
    )
    print(
        "Fallback setup: create browser.json with 'ytmusicapi browser' using the "
        "current Chrome/Edge request-header method."
    )
    return None


def main() -> None:
    try:
        requested_date = prompt_for_date()
        resolved_date, entries = resolve_chart_date(requested_date)
    except ValueError as error:
        print(f"Input error: {error}")
        return
    except requests.HTTPError as error:
        print(f"Chart request failed: {error}")
        return
    except requests.RequestException as error:
        print(f"Network error: {error}")
        return
    except Exception as error:
        print(f"Unable to scrape the chart: {error}")
        return

    if resolved_date != requested_date:
        print(
            "No chart was available for "
            f"{format_chart_date(requested_date)}. Using the nearest available chart date: "
            f"{format_chart_date(resolved_date)}."
        )
    else:
        print(f"Using chart date: {format_chart_date(resolved_date)}.")

    print_chart_entries(entries)

    project_dir = Path(__file__).resolve().parent
    yt = create_authenticated_ytmusic(project_dir)
    if yt is None:
        return

    playlist_title = f"{format_chart_date(resolved_date)} Billboard 100"
    try:
        playlist_id, existing_video_ids, created_new_playlist = create_or_reuse_playlist(
            yt, project_dir, playlist_title
        )
    except YouTubeQuotaExceededError as error:
        print("\nYouTube API quota is exhausted before the playlist could be loaded.")
        print(f"Quota message: {error.message}")
        print("Run the script again after the daily quota resets.")
        return

    if created_new_playlist:
        print(f"\nCreated private playlist: {playlist_title}")
    else:
        print(f"\nUsing existing playlist: {playlist_title}")

    added_count, skipped_duplicates, failed_count = add_songs_to_playlist(
        yt, project_dir, playlist_id, entries, existing_video_ids
    )

    print("\nPlaylist sync complete.")
    print(f"Added songs: {added_count}")
    print(f"Skipped duplicates: {skipped_duplicates}")
    print(f"Skipped failures: {failed_count}")
    print(f"YouTube Music playlist: {playlist_title}")


if __name__ == "__main__":
    load_dotenv()
    main()
