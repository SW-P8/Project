import pytest
import config
import json
import os

from copy import deepcopy
from datetime import datetime, timedelta
from unittest.mock import patch
from onlinedtc.onlinerunner import RunCleaning
from math import ceil
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.noise_correction import NoiseCorrection
from DTC.distance_calculator import DistanceCalculator
from matplotlib import pyplot as plt
import matplotlib.patches as patches


@pytest.fixture(autouse=True)
def cleanup():
    yield
    file_path = 'cleaned_trajectories.json'
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def trajectory():
    t = Trajectory()
    for i in range(30):
        t.add_point(i * 0.0001, 0.0001, datetime(2020, 6, 1, 0, 0, 0))
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


def test_clean_and_increment_calls_noise_detection(clean_runner, point_cloud):
    # Arrange
    clean_runner.read_trajectories(point_cloud)

    # Act
    with patch.object(NoiseCorrection, 'noise_detection') as mock_noise_detection:
        with patch.object(RunCleaning, '_append_to_json') as mock_append_to_json:
            clean_runner.clean_and_increment()

    # Assert
    assert 10 == mock_noise_detection.call_count
    assert 10 == mock_append_to_json.call_count


def test_append_to_json_creates_file(clean_runner, trajectory):
    # Arrange
    path_to_file = 'cleaned_trajectories.json'

    # Act
    clean_runner._append_to_json(trajectory)
    with open(path_to_file, 'r') as file:
        result = json.load(file)

    # Assert
    assert result is not None


def test_append_to_json_empty_trajectory_returns(clean_runner):
    # Arrange
    path_to_file = 'cleaned_trajectories.json'
    trajectory = Trajectory()

    # Act + Assert
    clean_runner._append_to_json(trajectory)


def test_clean_and_iterate_builds_new_safe_area(clean_runner):
    # Arrange
    local_point_cloud = TrajectoryPointCloud()
    for _ in range(50):
        t = Trajectory()
        t.add_point(0.0001, 0.0001, datetime.now())
        for i in range(45):
            t.add_point(i * 0.0001, 0.001, datetime.now())
            t.add_point(i * 0.0001, 0.0001, datetime.now())
        t.add_point(0.0001, 0.0001, datetime.now())
        local_point_cloud.add_trajectory(t)
    
    clean_runner.read_trajectories(local_point_cloud)
    # Act
    clean_runner.clean_and_increment()

    # Assert
    pass

def test_clean_and_iterate_delete_unused_safe_areas(clean_runner):
    local_points_cloud = TrajectoryPointCloud()
    t = Trajectory()
    t.add_point(0, 0, datetime(2025, 1, 1, 1, 1, 1))
    local_points_cloud.add_trajectory(t)

    clean_runner.read_trajectories(local_points_cloud)
    old_safe_areas = deepcopy(clean_runner.grid_system.safe_areas)

    clean_runner.clean_and_increment()

    assert clean_runner.grid_system.safe_areas != old_safe_areas
    assert clean_runner.grid_system.safe_areas == {}

def test_clean_and_iterate_add_appendage_road(clean_runner):
    # Arrange
    local_point_cloud = TrajectoryPointCloud()
    t = Trajectory()
    t2 = Trajectory()
    for i in range(30):
        t.add_point(i * 0.00005, 0.0001, datetime.now())
        t2.add_point(i * 0.00005, 0.0001, datetime.now())
    for i in range(30):
        t.add_point(0.0015, i* 0.0001 + 0.0001, datetime.now())
        t2.add_point(i * 0.00005 + 0.0015, 0.0001, datetime.now())
    for _ in range(50):
        local_point_cloud.add_trajectory(deepcopy(t))
        local_point_cloud.add_trajectory(deepcopy(t2))
    

    clean_runner.read_trajectories(local_point_cloud)

    clean_runner.clean_and_increment()

def test_clean_and_iterate_bend_road(clean_runner):
    # Create scatter plot
    fig, ax = plt.subplots()

    # Add circles to represent the radii of the safe areas
    for coords, safe_area in clean_runner.grid_system.safe_areas.items():
        x, y = coords
        radius = round(safe_area.radius)
        ax.scatter(x, y)
        circle = patches.Circle((x, y), radius, fill=False, edgecolor='r')
        ax.add_patch(circle)
        ax.annotate(f'({x}, {y})\nRadius: {radius}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')

    # Add labels and title
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Scatter Plot of Safe Area Coordinates with Radii')

    # Optionally, add annotations to the points
    for coords in clean_runner.grid_system.safe_areas.keys():
        x, y = coords
        plt.annotate(f'({x}, {y})', (x, y), textcoords="offset points", xytext=(0,10), ha='center')

    # Set the aspect of the plot to be equal, so circles are not distorted
    ax.set_aspect('equal', 'box')

    # Save plot to a file
    plt.savefig('safe_area_coordinates_with_radii.png')

    # Clear the plot to free memory
    plt.clf()
    # Arrange
    local_point_cloud = TrajectoryPointCloud()
    t = Trajectory()
    for i in range(30):
        t.add_point(i * 0.00005, 0.0001, datetime.now() + timedelta(minutes=i * 5))
    for i in range(60):
        t.add_point(0.0015, i* 0.0001 + 0.0001, datetime.now() + timedelta(minutes=i * 5))
    for i in range(120):
        t2 = deepcopy(t)
        for point in t2.points:
            point.timestamp = point.timestamp + timedelta(hours=i * 0.2)
        local_point_cloud.add_trajectory(deepcopy(t2))
    

    clean_runner.read_trajectories(local_point_cloud)

    clean_runner.clean_and_increment()

    # Create scatter plot
    fig, ax = plt.subplots()

    # Add circles to represent the radii of the safe areas
    for coords, safe_area in clean_runner.grid_system.safe_areas.items():
        x, y = coords
        radius = round(safe_area.radius)
        ax.scatter(x, y)
        circle = patches.Circle((x, y), radius, fill=False, edgecolor='r')
        ax.add_patch(circle)
        ax.annotate(f'({x}, {y})\nRadius: {radius}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')

    # Add labels and title
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Scatter Plot of Safe Area Coordinates with Radii')

    # Set the aspect of the plot to be equal, so circles are not distorted
    ax.set_aspect('equal', 'box')

    # Save plot to a file
    plt.savefig('safe_area_coordinates_with_radii_after.png')

    # Clear the plot to free memory
    plt.clf()