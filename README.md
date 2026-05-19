# Daily Data Dashboard

Fetches data from OpenWeatherMap, CoinGecko, and the GitHub API, then appends a snapshot row to a CSV file.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set your values:

```bash
copy .env.example .env
```

| Variable | Description |
|----------|-------------|
| `OPENWEATHER_API_KEY` | Free key from [OpenWeatherMap](https://openweathermap.org/api) |
| `WEATHER_CITY` | City name for weather (default: `London`) |
| `GITHUB_USERNAME` | Public GitHub username (default: `smart0303`) |

## Usage

```bash
python fetch_data.py
```

Each run appends one row to `output/daily_dashboard.csv`. The first run creates the file with a header row.

## APIs

| Source | Endpoint | Auth |
|--------|----------|------|
| Weather | `http://api.openweathermap.org/data/2.5/weather` | API key |
| Crypto | `https://api.coingecko.com/api/v3/simple/price` | None |
| GitHub | `https://api.github.com/users/{username}` | None (public) |

## CSV columns

`fetched_at`, `weather_city`, `weather_temp_c`, `weather_feels_like_c`, `weather_humidity_pct`, `weather_description`, `btc_price_usd`, `eth_price_usd`, `github_username`, `github_name`, `github_public_repos`, `github_followers`, `github_following`
