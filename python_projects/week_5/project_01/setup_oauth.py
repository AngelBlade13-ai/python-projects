from __future__ import annotations

import argparse
import os
import webbrowser
from pathlib import Path

from ytmusicapi.auth.oauth.credentials import OAuthCredentials
from ytmusicapi.auth.oauth.token import RefreshingToken, Token


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create oauth.json for the Music Time Machine project."
    )
    parser.add_argument(
        "--file",
        default="oauth.json",
        help="Path where the OAuth token should be written. Defaults to oauth.json.",
    )
    parser.add_argument(
        "--client-id",
        default=os.getenv("YTMUSIC_CLIENT_ID"),
        help="Google OAuth client ID. Defaults to YTMUSIC_CLIENT_ID.",
    )
    parser.add_argument(
        "--client-secret",
        default=os.getenv("YTMUSIC_CLIENT_SECRET"),
        help="Google OAuth client secret. Defaults to YTMUSIC_CLIENT_SECRET.",
    )
    return parser.parse_args()


def prompt_missing(value: str | None, label: str) -> str:
    if value:
        return value

    return input(f"Enter your Google YouTube Data API {label}: ").strip()


def main() -> None:
    args = parse_args()
    client_id = prompt_missing(args.client_id, "client ID")
    client_secret = prompt_missing(args.client_secret, "client secret")

    credentials = OAuthCredentials(client_id, client_secret)
    code = credentials.get_code()
    auth_url = f"{code['verification_url']}?user_code={code['user_code']}"

    print(f"Opening browser for OAuth setup: {auth_url}")
    webbrowser.open(auth_url)
    input("Finish the login flow, then press Enter here. Press Ctrl+C to abort.")

    raw_token = credentials.token_from_code(code["device_code"])
    token_fields = set(Token.members())
    filtered_token = {
        key: value
        for key, value in raw_token.items()
        if key in token_fields
    }

    token = RefreshingToken(credentials=credentials, **filtered_token)
    token.update(token.as_dict())

    output_path = Path(args.file)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path

    token.store_token(str(output_path))
    print(f"Created {output_path.resolve()}")


if __name__ == "__main__":
    main()
