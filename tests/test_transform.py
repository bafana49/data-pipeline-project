import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from transform import transform_to_dataframe

def make_sample_raw_data():
    """Create a sample raw data dictionary mimicking the Open-Meteo API response."""
    return {
        "daily": {
            "time": ["2024-01-01", "2024-01-02", "2024-01-02"],  # duplicate date
            "temperature_2m_max": [25.0, 26.5, 26.5],
            "temperature_2m_min": [15.0, 16.0, 16.0],
            "precipitation_sum": [0.0, 5.0, 5.0],
            "windspeed_10m_max": [10.0, 12.5, 12.5],
        }
    }

def test_transform_returns_dataframe():
    raw_data = make_sample_raw_data()
    df = transform_to_dataframe(raw_data)
    assert isinstance(df, pd.DataFrame)

def test_transform_removes_duplicates():
    raw_data = make_sample_raw_data()
    df = transform_to_dataframe(raw_data)
    assert len(df) == 2  # Should remove the duplicate

def test_transform_adds_temp_range_column():
    raw_data = make_sample_raw_data()
    df = transform_to_dataframe(raw_data)
    assert "temp_range_c" in df.columns
    assert df.iloc[0]["temp_range_c"] == 10.0 # 25.0 - 15.0

def test_transform_sorts_by_date():
    raw_data = make_sample_raw_data()
    df = transform_to_dataframe(raw_data)
    assert df["date"].is_monotonic_increasing