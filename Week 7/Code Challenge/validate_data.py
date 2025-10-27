# validate_data.py
import pandas as pd

# Load the sampled CSVs produced before running pytest
weather_df = pd.read_csv("sampled_weather_df.csv")
field_df = pd.read_csv("sampled_field_df.csv")


def test_read_weather_DataFrame_shape():
    """Weather DataFrame should not be empty and have rows/columns."""
    assert weather_df.shape[0] > 0, "Weather DataFrame has no rows"
    assert weather_df.shape[1] > 0, "Weather DataFrame has no columns"


def test_read_field_DataFrame_shape():
    """Field DataFrame should not be empty and have rows/columns."""
    assert field_df.shape[0] > 0, "Field DataFrame has no rows"
    assert field_df.shape[1] > 0, "Field DataFrame has no columns"


def test_weather_DataFrame_columns():
    """Weather DataFrame should contain expected columns."""
    expected_cols = {"Weather_station_ID", "Message", "Measurement", "Value"}
    assert expected_cols.issubset(set(weather_df.columns)), \
        f"Missing columns in weather_df. Found: {weather_df.columns}"


def test_field_DataFrame_columns():
    """Field DataFrame should contain expected columns."""
    expected_cols = {"Field_ID", "Elevation", "Crop_type"}
    assert expected_cols.issubset(set(field_df.columns)), \
        f"Missing columns in field_df. Found: {field_df.columns}"


def test_field_DataFrame_non_negative_elevation():
    """Elevation values in field DataFrame should be non-negative."""
    assert (field_df["Elevation"] >= 0).all(), "Negative elevation values found"


def test_crop_types_are_present():
    """Check that cassava, wheat, and tea exist in the Crop_type column."""
    expected_crops = {"cassava", "wheat", "tea"}
    crop_types_in_data = set(field_df["Crop_type"].unique())
    missing_crops = expected_crops - crop_types_in_data
    assert not missing_crops, f"Missing crop types: {missing_crops}"



def test_positive_rainfall_values():
    """Rainfall measurements should always be positive."""
    rainfall_df = weather_df[weather_df["Measurement"] == "Rainfall"]
    assert (rainfall_df["Value"] > 0).all(), "Non-positive rainfall values found"
