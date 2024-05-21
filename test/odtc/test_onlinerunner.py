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
from DTC.construct_safe_area import ConstructSafeArea
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

@pytest.fixture
def initial_model(point_cloud):
    gs = GridSystem(point_cloud)
    gs.create_grid_system()
    gs.extract_main_route()
    min_pts = ceil(len(gs.main_route) * config.min_pts_from_mr)
    smoothed_main_route = RouteSkeleton.smooth_main_route(gs.main_route)
    filtered_main_route = RouteSkeleton.graph_based_filter(data=smoothed_main_route, min_pts=min_pts)
    route_skeleton = RouteSkeleton.filter_sparse_points(filtered_main_route, config.distance_interval)
    safe_areas = ConstructSafeArea.construct_safe_areas(route_skeleton, gs.grid)
    return safe_areas, gs.initialization_point, smoothed_main_route

def test_init_when_filled_grid_should_build_class(initial_model):
    # Arrange
    safe_areas, initialization_point, smoothed_main_route = initial_model

    # Act
    result = RunCleaning(safe_areas, initialization_point, smoothed_main_route)

    # Assert
    assert result is not None


@pytest.fixture
def clean_runner(initial_model):
    safe_areas, initialization_point, smoothed_main_route = initial_model

    cr = RunCleaning(safe_areas, initialization_point, smoothed_main_route)
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
    t2 = Trajectory()
    t2.add_point(0, 0, datetime(2026, 1, 1, 1, 1, 1))
    local_points_cloud.add_trajectory(t)
    local_points_cloud.add_trajectory(t2)

    clean_runner.read_trajectories(local_points_cloud)
    old_safe_areas = deepcopy(clean_runner.safe_areas)

    clean_runner.clean_and_increment()

    assert clean_runner.safe_areas != old_safe_areas
    assert len(clean_runner.safe_areas) == 1

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

@pytest.mark.skip
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
        t.add_point(i * 0.00005, 0.0001, datetime.now() + timedelta(minutes=i * 3))
    for i in range(60):
        t.add_point(0.0015, i * 0.0001 + 0.0001, datetime.now() + timedelta(minutes=i * 3))
    for i in range(100):
        t2 = deepcopy(t)
        for point in t2.points:
            point.timestamp = point.timestamp + timedelta(minutes=i * 20)
        local_point_cloud.add_trajectory(deepcopy(t2))

    trajectory = deepcopy(local_point_cloud.trajectories[2])

    clean_runner.read_trajectories(local_point_cloud)

    clean_runner.clean_and_increment()

    # Create scatter plot
    fig, ax = plt.subplots()

    points = [DistanceCalculator.calculate_exact_index_for_point(
        point, clean_runner.grid_system.initialization_point) for point in trajectory.points]
    trajectory_x = [point[0] for point in points]
    trajectory_y = [point[1] for point in points]
    ax.plot(trajectory_x, trajectory_y, marker='o',
            linestyle='-', color='black', label='Trajectory', alpha=1, markersize=1)

    # Add circles to represent the radii of the safe areas
    for coords, safe_area in clean_runner.grid_system.safe_areas.items():
        x, y = coords
        radius = round(safe_area.radius)
        ax.scatter(x, y, s=50, marker='^')
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