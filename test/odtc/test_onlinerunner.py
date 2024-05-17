import pytest
import config

from unittest.mock import patch
from onlinedtc.onlinerunner import RunCleaning
from math import ceil
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.noise_correction import NoiseCorrection


@pytest.fixture
def trajectory():
    t = Trajectory()
    for i in range(10):
        t.add_point(i, i)
    return t


@pytest.fixture
def point_cloud(trajectory):
    pc = TrajectoryPointCloud()
    for _ in range(10):
        pc.add_trajectory(trajectory)
    return pc


def test_init_no_grid_raises_error(point_cloud):
    # Arrange
    grid_system = GridSystem(point_cloud)
    smooth_main_route = set()

    # Act + Assert
    with pytest.raises(AttributeError):
        RunCleaning(grid_system, smooth_main_route)


@pytest.fixture
def grid_system(point_cloud):
    gs = GridSystem(point_cloud)
    rs = RouteSkeleton()
    gs.create_grid_system()
    gs.extract_main_route()
    min_pts = ceil(len(gs.main_route) * config.min_pts_from_mr)
    smr = rs.smooth_main_route(gs.main_route)
    fmr = rs.graph_based_filter(data=smr, min_pts=min_pts)
    gs.route_skeleton = rs.filter_sparse_points(fmr, config.distance_interval)
    gs.construct_safe_areas()
    return gs, smr


def test_init_when_filled_grid_should_build_class(grid_system):
    # Arrange
    gs, smr = grid_system

    # Act
    result = RunCleaning(gs, smr)

    # Assert
    assert result is not None


@pytest.fixture
def clean_runner(grid_system):
    gs, smr = grid_system
    cr = RunCleaning(gs, smr)
    return cr


def test_read_trajectories_read_ten_trajectory(clean_runner, point_cloud):
    # Act
    clean_runner.read_trajectories(point_cloud)

    # Assert
    assert 10 == len(clean_runner.input_trajectories)


def test_read_trajectory_read_one_trajectory(clean_runner, trajectory):
    # Arrange
    point_cloud = TrajectoryPointCloud()
    point_cloud.add_trajectory(trajectory)

    # Act
    clean_runner.read_trajectories(point_cloud)

    # Assert
    assert 1 == len(clean_runner.input_trajectories)


def test_read_trajectory_read_no_trajectory(clean_runner):
    # Arrange
    point_cloud = TrajectoryPointCloud()

    # Act
    clean_runner.read_trajectories(point_cloud)

    # Assert
    assert 0 == len(clean_runner.input_trajectories)

@patch.object(NoiseCorrection, 'noise_detection')
@patch.object(RunCleaning, '_append_to_json')
def test_clean_and_increment_calls_noise_detection(clean_runner, point_cloud, mock_noise_detection, mock_append_to_json):
    # Arrange
    clean_runner.read_trajectories(point_cloud)

    # Act
    clean_runner.clean_and_increment()

    # Assert
    mock_noise_detection.assert_called_once()
