import pytest
import pandas as pd
import database.load_data as load_data

@pytest.fixture
def data():
    df = pd.DataFrame(columns=['taxi_id', 'date_time', 'longitude', 'latitude'])
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
    df["date_time"] = pd.to_datetime(df["date_time"])

    return df


@pytest.fixture
def create_erroneous_outercity_data(data):
    df = data
    df['longitude'] = [115.43, 115.44, 115.45, 115.46, 115.47, 115.48, 115.49, 115.50, -190.00, 115.52]
    df['latitude'] = [40.50, 90.00, 40.51, 40.52, 40.53, 40.54, 40.55, 40.56, 40.57-0, 40.58]
    return df

@pytest.fixture
def create_erroneous_innercity_data(data):
    df = data
    df['longitude'] = [116.350000, 116.355000, 116.360000, 116.365000, 116.370000, 116.375000, 116.380000, 116.385000, 116.390000, 115.55000]
    df['latitude'] = [39.870000, 39.875000, 39.880000, 39.885000, 39.890000, 39.895000, 39.900000, 39.905000, 39.910000, 39.440000]
    return df

@pytest.fixture
def create_erroneous_beijing_data(data):
    df = data
    df['longitude'] = [116.45, 116.48, 116.51, 116.53, 116.47, 116.50, 116.49, 116.52, 116.46, 116.20]
    df['latitude'] = [39.85, 39.82, 39.89, 39.78, 39.84, 39.81, 39.88, 39.79, 39.86, 40.00]
    return df

@pytest.fixture
def create_correct_data(data):
    df = data
    df['date_time'] = [
        "2024-03-14 00:00:00",
        "2024-03-14 00:02:00",
        "2024-03-14 00:04:00",
        "2024-03-14 00:06:00",
        "2024-03-14 00:08:00",
        "2024-03-14 00:21:00",
        "2024-03-14 00:23:00",
        "2024-03-14 00:25:00",
        "2024-03-14 00:27:00",
        "2024-03-14 00:38:00"
    ]
    df["date_time"] = pd.to_datetime(df["date_time"])
    df['longitude'] = [116.350000, 116.355000, 116.360000, 116.365000, 116.370000, 116.375000, 116.380000, 116.385000, 116.390000, 116.395000]
    df['latitude'] = [39.870000, 39.875000, 39.880000, 39.885000, 39.890000, 39.895000, 39.900000, 39.905000, 39.910000, 39.915000]
    return df

def test_transform_data_When_given_dataframe_with_errors_Should_return_cleaned_dataframe(create_erroneous_outercity_data):
    # Arrange
    test_trajectory_id = 1
    # Act
    result = load_data._transform_data(create_erroneous_outercity_data, test_trajectory_id, "full")
    # Assert
    assert result.shape == (8, 5) # There are two erroneus coordinate points, so there sould only be 8 rows
    assert result['trajectory_id'].nunique() == 2 # There should be two distinct trajectories for taxi 1

def test_transform_data_innercity_when_given_dataframe_with_errors_should_return_cleaned_dataframe(create_erroneous_innercity_data):
    # Arrange
    test_trajectory_id = 1
    expected_longitude = [116.350000, 116.360000, 116.355000, 116.365000, 116.370000, 116.375000, 116.380000, 116.385000, 116.390000]
    expected_latitude = [39.870000, 39.880000, 39.875000, 39.885000, 39.890000, 39.895000, 39.900000, 39.905000, 39.910000]

    # Act
    result = load_data._transform_data(create_erroneous_innercity_data, test_trajectory_id, "inner")
    

    # Assert
    assert result.shape == (9, 5)
    assert result['trajectory_id'].nunique() == 2
    assert result['longitude'].tolist() == expected_longitude
    assert result['latitude'].tolist() == expected_latitude

def test_transform_data_when_given_correct_data_should_not_change_anything(create_correct_data):
    # Arrange
    test_trajectory_id = 1
    expected_longitude = [116.350000, 116.355000, 116.360000, 116.365000, 116.370000, 116.375000, 116.380000, 116.385000, 116.390000, 116.395000]
    expected_latitude = [39.870000, 39.875000, 39.880000, 39.885000, 39.890000, 39.895000, 39.900000, 39.905000, 39.910000, 39.915000]

    # Act
    resultInner = load_data._transform_data(create_correct_data, test_trajectory_id, "inner")
    resultOuter = load_data._transform_data(create_correct_data, test_trajectory_id, "full")

    # Assert
    assert resultInner.shape == (10, 5)
    assert resultOuter.shape == (10, 5)

    assert resultInner['trajectory_id'].nunique() == 2
    assert resultOuter['trajectory_id'].nunique() == 2

    assert resultInner['longitude'].tolist() == expected_longitude
    assert resultOuter['longitude'].tolist() == expected_longitude

    assert resultInner['latitude'].tolist() == expected_latitude
    assert resultOuter['latitude'].tolist() == expected_latitude

def test_transform_data_beijing_when_data_with_errors_should_return_cleaned_dataframe(create_erroneous_beijing_data):
    # Arrange
    test_trajectory_id = 1
    expected_longitude = [116.45, 116.51, 116.48, 116.53, 116.47, 116.50, 116.49, 116.52, 116.46]
    expected_latitude = [39.85, 39.89, 39.82, 39.78, 39.84, 39.81, 39.88, 39.79, 39.86]

    # Act
    result = load_data._transform_data(create_erroneous_beijing_data, test_trajectory_id, "city")
    
    # Assert
    assert (9, 5) == result.shape
    assert 2 == result['trajectory_id'].nunique()
    assert expected_longitude == result['longitude'].tolist()
    assert expected_latitude == result['latitude'].tolist()

