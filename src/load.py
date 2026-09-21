"""
load.py
Loads the cleaned weather CSV into a SQLite database, with basic validation.
"""

import sqlite3
import pandas as pd
from pathlib import Path

PROCESSED_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "weather.db"
CSV_PATH = PROCESSED_DATA_DIR / "weather_clean.csv"


def validate_data(df: pd.DataFrame) -> None:
    """Run basic sanity checks before loading. Raises if something looks wrong."""
    if len(df) == 0:
        raise ValueError("Validation failed: DataFrame is empty.")

    required_columns = {
        "date", "temp_max_c", "temp_min_c",
        "precipitation_mm", "windspeed_max_kmh", "temp_range_c"
    }
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Validation failed: missing columns {missing}")

    key_cols = ["date", "temp_max_c", "temp_min_c"]
    if df[key_cols].isnull().any().any():
        raise ValueError("Validation failed: nulls found in key columns.")

    if (df["temp_max_c"] < df["temp_min_c"]).any():
        raise ValueError("Validation failed: temp_max_c is less than temp_min_c on some rows.")

    print(f"Validation passed: {len(df)} rows, all checks OK.")


def load_to_sqlite(df: pd.DataFrame, db_path: Path, table_name: str = "weather") -> None:
    """Load the DataFrame into a SQLite table, replacing any existing table."""
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded {len(df)} rows into table '{table_name}' at {db_path}")
    finally:
        conn.close()


def main():
    print(f"Reading processed data from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, parse_dates=["date"])

    validate_data(df)
    load_to_sqlite(df, DB_PATH)

    # Quick confirmation query
    conn = sqlite3.connect(DB_PATH)
    result = conn.execute("SELECT COUNT(*) FROM weather").fetchone()
    print(f"Row count in database: {result[0]}")
    conn.close()


if __name__ == "__main__":
    main()