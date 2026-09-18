"""
extract.py
Pulls raw weather data from the Open-Meteo API and saves it to data/raw/.
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Config — feel free to change city/coordinates
LATITUDE = -33.9249   # Cape Town
LONGITUDE = 18.4241
DAYS_BACK = 30

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_weather_data(latitude: float, longitude: float, days_back: int) -> dict:
    """Fetch historical daily weather data from Open-Meteo."""
    end_date = datetime.utcnow().date() - timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_data(data: dict, output_dir: Path) -> Path:
    """Save the raw JSON response with a timestamped filename."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"weather_raw_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    return output_path


def main():
    print("Fetching weather data...")
    data = fetch_weather_data(LATITUDE, LONGITUDE, DAYS_BACK)
    output_path = save_raw_data(data, RAW_DATA_DIR)
    print(f"Saved raw data to: {output_path}")


if __name__ == "__main__":
    main()