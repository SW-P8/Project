# These tests will test if the cleaning part of the system can trigger safe-area updating.
from DTC.trajectory import Trajectory
from DTC.noise_correction import NoiseCorrection
from DTC.construct_safe_area import SafeArea
from DTC.distance_calculator import DistanceCalculator
from unittest.mock import patch
from copy import deepcopy
from datetime import datetime
import pytest
import threading


@pytest.fixture
def safe_areas():
    safe_areas = {}
    for i in range(5):
        safe_areas[(i * 2.5, i * 2.5)] = SafeArea.from_meta_data((i * 2.5, i * 2.5), 2, 10)
    safe_areas[1000, 1000] = SafeArea.from_meta_data((1000, 1000), 2, 10)
    return safe_areas


@pytest.fixture
def noise_corrector(safe_areas):
    initialization_point = (0, 0)
    return NoiseCorrection(safe_areas, initialization_point)


@pytest.fixture
def trajectory_off_one_direction():
    trajectory = Trajectory()
    trajectory.add_point(180, 90, datetime.now())
    trajectory.add_point(180, 90, datetime.now())
    trajectory.add_point(180, 90, datetime.now())
    return trajectory


@pytest.fixture
def trajectory_off_two_direction(trajectory_off_one_direction):
    trajectory = trajectory_off_one_direction
    trajectory.add_point(-180, -90, datetime.now())
    trajectory.add_point(-180, -90, datetime.now())
    trajectory.add_point(-180, -90, datetime.now())
    return trajectory


def test_noise_correction_calls_update(noise_corrector, trajectory_off_one_direction):
    # Arrange + Act
    with patch.object(noise_corrector, '_update_safe_areas_thread') as mock_update:
        for _ in range(100):
            noise_corrector.noise_detection(deepcopy(trajectory_off_one_direction))

    # Assert
    mock_update.assert_called()


def test_noise_correction_does_not_call_update(noise_corrector, trajectory_off_one_direction):
    # Arrange + Act
    with patch.object(noise_corrector, '_update_safe_areas_thread') as mock_update:
        noise_corrector.noise_detection(deepcopy(trajectory_off_one_direction))

    # Assert
    mock_update.assert_not_called()


def test_noise_correction_creates_threads(safe_areas, trajectory_off_one_direction):
    # Arrange
    initialization_point = (0, 1)
    noise_corrector = NoiseCorrection(safe_areas, initialization_point)
    num_of_threads_before = threading.active_count()

    # Act
    with patch.object(noise_corrector, 'update_safe_area') as mock_update_safe_area:
        for _ in range(2):
            noise_corrector.noise_detection(deepcopy(trajectory_off_one_direction))
    num_of_threads_after = threading.active_count()

    # Assert
    mock_update_safe_area.assert_called()
    # Threads should be closed.
    assert 0 == num_of_threads_before - num_of_threads_after
    assert 1 == mock_update_safe_area.call_count
    # Assert that the safe area is removed.
    assert (1000, 1000) not in safe_areas.keys()


def test_noise_correction_creates_two_threads(safe_areas, trajectory_off_two_direction):
    # Arrange
    DistanceCalculator.convert_cell_to_point((0, 1), (10, 10))
    initialization_point = (0, 0)
    noise_corrector = NoiseCorrection(
        safe_areas, initialization_point)
    num_of_threads_before = threading.active_count()

    # Act
    with patch.object(noise_corrector, 'update_safe_area') as mock_update_safe_area:
        for _ in range(2):
            noise_corrector.noise_detection(
                deepcopy(trajectory_off_two_direction))
    num_of_threads_after = threading.active_count()

    # Assert
    mock_update_safe_area.assert_called()
    # Threads should be closed.
    assert 0 == num_of_threads_before - num_of_threads_after
    assert 2 == mock_update_safe_area.call_count
    # Assert that the correct safe-areas are removed.
    assert (0, 0) not in safe_areas.keys()
    assert (1000, 1000) not in safe_areas.keys()
