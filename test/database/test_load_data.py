import pytest
import pandas as pd
import database.load_data as load_data

@pytest.fixture
def create_erroneous_dataframe():
    df = pd.DataFrame()
    df['taxi_id'] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    df['date_time'] = [
        "2024-03-14 00:00:00",
        "2024-03-14 00:04:00",
        "2024-03-14 00:02:00",
        "2024-03-14 00:06:00",
        "2024-03-14 00:08:00",
        "2024-03-14 00:21:00",
        "2024-03-14 00:23:00",
        "2024-03-14 00:25:00",
        "2024-03-14 00:27:00",
        "2024-03-14 00:38:00"
    ]
    df['longitude'] = [115.43, 115.44, 115.45, 115.46, 115.47, 115.48, 115.49, 115.50, -190.00, 115.52]
    df['latitude'] = [40.50, 90.00, 40.51, 40.52, 40.53, 40.54, 40.55, 40.56, 40.57-0, 40.58]
    df["date_time"] = pd.to_datetime(df["date_time"])
    return df



def test_transform_data_When_given_dataframe_with_errors_Should_return_cleaned_dataframe(create_erroneous_dataframe):
    # Arrange
    test_trajectory_id = 1
    # Act
    result = load_data.__transform_data(create_erroneous_dataframe, test_trajectory_id)
    # Assert
    assert result.shape == (8, 5) # There are two erroneus coordinate points, so there sould only be 8 rows
    assert result['trajectory_id'].nunique() == 2 # There should be two distinct trajectories for taxi 1
