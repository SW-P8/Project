# These tests will test if the cleaning part of the system can trigger safe-area updating.
from DTC.trajectory import Trajectory
from DTC.noise_correction import NoiseCorrection
from DTC.construct_safe_area import SafeArea
from unittest.mock import patch
from copy import deepcopy
from datetime import datetime
import pytest


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
    with patch.object(noise_corrector, '_update_safe_areas') as mock_update:
        for _ in range(100):
            noise_corrector.noise_detection(deepcopy(trajectory_off_one_direction))

    # Assert
    mock_update.assert_called()


def test_noise_correction_does_not_call_update(noise_corrector, trajectory_off_one_direction):
    # Arrange + Act
    with patch.object(noise_corrector, '_update_safe_areas') as mock_update:
        noise_corrector.noise_detection(deepcopy(trajectory_off_one_direction))

    # Assert
    mock_update.assert_not_called()
