"""
transform.py
Cleans and reshapes the raw weather JSON into a tidy CSV in data/processed/.
"""

import json
import glob
import pandas as pd
from pathlib import Path

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def get_latest_raw_file(raw_dir: Path) -> Path:
    """Find the most recently created raw JSON file."""
    files = sorted(glob.glob(str(raw_dir / "weather_raw_*.json")))
    if not files:
        raise FileNotFoundError("No raw weather files found. Run extract.py first.")
    return Path(files[-1])


def load_raw_data(file_path: Path) -> dict:
    with open(file_path) as f:
        return json.load(f)


def transform_to_dataframe(raw_data: dict) -> pd.DataFrame:
    """Convert the nested JSON 'daily' block into a flat, clean DataFrame."""
    daily = raw_data["daily"]

    df = pd.DataFrame({
        "date": daily["time"],
        "temp_max_c": daily["temperature_2m_max"],
        "temp_min_c": daily["temperature_2m_min"],
        "precipitation_mm": daily["precipitation_sum"],
        "windspeed_max_kmh": daily["windspeed_10m_max"],
    })

    df["date"] = pd.to_datetime(df["date"])

    # Drop rows missing critical fields
    df = df.dropna(subset=["date", "temp_max_c", "temp_min_c"])

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Derived column: daily temperature range
    df["temp_range_c"] = df["temp_max_c"] - df["temp_min_c"]

    df = df.sort_values("date").reset_index(drop=True)
    return df


def save_processed_data(df: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "weather_clean.csv"
    df.to_csv(output_path, index=False)
    return output_path


def main():
    raw_file = get_latest_raw_file(RAW_DATA_DIR)
    print(f"Loading raw data from: {raw_file}")

    raw_data = load_raw_data(raw_file)
    df = transform_to_dataframe(raw_data)

    output_path = save_processed_data(df, PROCESSED_DATA_DIR)
    print(f"Saved {len(df)} clean rows to: {output_path}")
    print(df.head())


if __name__ == "__main__":
    main()