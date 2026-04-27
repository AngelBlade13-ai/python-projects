# Project 01: Musical Time Machine

This project asks for a past date, scrapes the Bakeboard Hot 100 chart for that day, prints the song list, and then creates a private YouTube playlist with those songs.

The original tutorial flow used `ytmusicapi browser`, which copies request headers from a logged-in browser session into `browser.json`. That can still work sometimes, but it is brittle because YouTube Music's private web endpoints can reject otherwise valid sessions with HTTP 400 errors. This project now prefers OAuth and falls back to the official YouTube Data API when YouTube Music's private endpoints fail.

## Files

- `main.py`
- `requirements.txt`
- `.gitignore`

## Setup

1. Open a terminal in this folder.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create OAuth credentials in Google Cloud.
4. In Google Cloud Console, enable the YouTube Data API v3.
5. Create an `OAuth client ID` and choose `TVs and Limited Input devices`.
6. Save the client ID and client secret.
7. Add the credentials to your environment or a local `.env` file:

```bash
YTMUSIC_CLIENT_ID=your_client_id
YTMUSIC_CLIENT_SECRET=your_client_secret
```

8. In this folder, run the project OAuth setup helper:

```bash
python setup_oauth.py
```

9. Follow the terminal prompts to create `oauth.json`.

## Optional Browser Auth

The old tutorial method was:

```bash
ytmusicapi browser
```

That command asks you to paste request headers copied from a logged-in `https://music.youtube.com` browser request, usually a successful `browse?...` request. If it works, it creates `browser.json`.

This is now treated as a fallback instead of the main setup path. In testing, `ytmusicapi` browser/OAuth sessions could authenticate but still fail on `get_library_playlists()`, `create_playlist()`, `search()`, or `add_playlist_items()` with `Server returned HTTP 400: Bad Request. Request contains an invalid argument.`

## Run

```bash
python main.py
```

Enter a date such as `2000-08-12`.

## Notes

- The script uses the tutorial mirror at `https://appbrewery.github.io/bakeboard-hot-100/{date}/`.
- If the exact date is missing, the script automatically searches for the nearest available chart date and tells you which date it used.
- The script prefers `oauth.json`. It also supports `browser.json` as a fallback for `ytmusicapi`.
- If `oauth.json` is present, you must also provide `YTMUSIC_CLIENT_ID` and `YTMUSIC_CLIENT_SECRET`.
- If no auth file is present, the script still scrapes and prints the chart but skips playlist creation.
- If YouTube Music rejects search or playlist requests, the script falls back to the official YouTube Data API using the same `oauth.json` token.
- The YouTube Data API has daily quota limits. Search requests are expensive, so a full 100-song playlist can hit quota before it finishes.
- If the playlist already exists in `playlist_cache.json` or can be found through YouTube, the script reuses it and avoids adding duplicate video IDs it finds in that playlist.
- Song search results are saved in `song_cache.json`, so reruns can reuse previous lookups and avoid spending quota on the same songs again.
- If quota is exhausted, wait for the daily quota reset and rerun the script. It will reuse cached playlist and song data.
- Some searches can fail or return no result; those songs are skipped so the rest of the playlist can still be created.
