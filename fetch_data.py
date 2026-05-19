import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

OUTPUT_DIR = Path(__file__).parent / "output"
CSV_FILENAME = "daily_dashboard.csv"

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
CRYPTO_URL = "https://api.coingecko.com/api/v3/simple/price"
GITHUB_URL = "https://api.github.com/users/{username}"

CSV_COLUMNS = [
    "fetched_at",
    "weather_city",
    "weather_temp_c",
    "weather_feels_like_c",
    "weather_humidity_pct",
    "weather_description",
    "btc_price_usd",
    "eth_price_usd",
    "github_username",
    "github_name",
    "github_public_repos",
    "github_followers",
    "github_following",
]


def fetch_weather(city: str, api_key: str) -> dict:
    response = requests.get(
        WEATHER_URL,
        params={"q": city, "appid": api_key, "units": "metric"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "weather_city": data["name"],
        "weather_temp_c": data["main"]["temp"],
        "weather_feels_like_c": data["main"]["feels_like"],
        "weather_humidity_pct": data["main"]["humidity"],
        "weather_description": data["weather"][0]["description"],
    }


def fetch_crypto() -> dict:
    response = requests.get(
        CRYPTO_URL,
        params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "btc_price_usd": data["bitcoin"]["usd"],
        "eth_price_usd": data["ethereum"]["usd"],
    }


def fetch_github(username: str) -> dict:
    response = requests.get(
        GITHUB_URL.format(username=username),
        headers={"Accept": "application/vnd.github+json"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "github_username": data["login"],
        "github_name": data.get("name") or "",
        "github_public_repos": data["public_repos"],
        "github_followers": data["followers"],
        "github_following": data["following"],
    }


def build_row(city: str, api_key: str, github_username: str) -> dict:
    row = {"fetched_at": datetime.now(timezone.utc).isoformat()}
    row.update(fetch_weather(city, api_key))
    row.update(fetch_crypto())
    row.update(fetch_github(github_username))
    return row


def export_to_csv(row: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OPENWEATHER_API_KEY is not set.")
        sys.exit(1)

    city = os.getenv("WEATHER_CITY", "London")
    github_username = os.getenv("GITHUB_USERNAME", "smart0303")

    print(f"Fetching data for {city}, crypto prices, and GitHub user @{github_username}...")

    try:
        row = build_row(city, api_key, github_username)
    except requests.HTTPError as e:
        print(f"API request failed: {e.response.status_code} {e.response.reason}")
        if e.response.text:
            print(e.response.text[:500])
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)

    output_path = OUTPUT_DIR / CSV_FILENAME
    export_to_csv(row, output_path)

    print(f"Exported to {output_path}")
    for key in CSV_COLUMNS:
        print(f"  {key}: {row[key]}")


if __name__ == "__main__":
    main()
