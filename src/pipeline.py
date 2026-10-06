"""
pipeline.py
Orchestrates the full ETL pipeline: extract -> transform -> load.
Run this single script to execute the entire data pipeline end to end.
"""

import logging
import sys

from extract import fetch_weather_data, save_raw_data, RAW_DATA_DIR, LATITUDE, LONGITUDE, DAYS_BACK
from transform import get_latest_raw_file, load_raw_data, transform_to_dataframe, save_processed_data, PROCESSED_DATA_DIR
from load import validate_data, load_to_sqlite, DB_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_extract():
    logger.info("Starting extract step...")
    try:
        data = fetch_weather_data(LATITUDE, LONGITUDE, DAYS_BACK)
        path = save_raw_data(data, RAW_DATA_DIR)
        logger.info(f"Extract complete. Raw data saved to {path}")
        return path
    except Exception as e:
        logger.error(f"Extract step failed: {e}")
        raise


def run_transform():
    logger.info("Starting transform step...")
    try:
        raw_file = get_latest_raw_file(RAW_DATA_DIR)
        raw_data = load_raw_data(raw_file)
        df = transform_to_dataframe(raw_data)
        path = save_processed_data(df, PROCESSED_DATA_DIR)
        logger.info(f"Transform complete. {len(df)} rows saved to {path}")
        return df
    except Exception as e:
        logger.error(f"Transform step failed: {e}")
        raise


def run_load(df):
    logger.info("Starting load step...")
    try:
        validate_data(df)
        load_to_sqlite(df, DB_PATH)
        logger.info("Load complete.")
    except Exception as e:
        logger.error(f"Load step failed: {e}")
        raise


def main():
    logger.info("=== Pipeline run started ===")
    try:
        run_extract()
        df = run_transform()
        run_load(df)
        logger.info("=== Pipeline run completed successfully ===")
    except Exception:
        logger.error("=== Pipeline run FAILED ===")
        sys.exit(1)


if __name__ == "__main__":
    main()