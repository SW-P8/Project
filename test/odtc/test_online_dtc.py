from onlinedtc.runner import create_trajectory_point_cloud, build_grid_system
from onlinedtc.runner import smooth_new_main_route, filter_smoothed_main_route
from onlinedtc.runner import update_safe_area
from DTC.trajectory import Trajectory, TrajectoryPointCloud, Point
from DTC.gridsystem import GridSystem
from DTC.construct_safe_area import SafeArea
import pytest
# I am lazy, so no mocking will happen here >:(


def test_create_trajectory_point_cloud_with_non_empty():
    # Arrange
    trajectory = Trajectory()
    for i in range(20):
        trajectory.add_point(1 + 0.1 * i, 1)

    # Act
    result = create_trajectory_point_cloud(trajectory)

    # Assert
    assert TrajectoryPointCloud == type(result)
    assert 20 == len(result.trajectories[0].points)


def test_create_trajectory_point_cloud_with_empty():
    # Arrange
    trajectory = Trajectory()

    # Act
    result = create_trajectory_point_cloud(trajectory)

    # Assert
    assert TrajectoryPointCloud == type(result)
    assert 0 == len(result.trajectories[0].points)


@pytest.fixture
def trajectory_point_cloud():
    trajectory = Trajectory()
    point_cloud = TrajectoryPointCloud()
    for i in range(20):
        trajectory.add_point(1 + 0.1 * i, 1)
    point_cloud.add_trajectory(trajectory)
    return point_cloud


def test_build_grid_system_with_data(trajectory_point_cloud):
    # Arrange
    initialization_point = (1, 1)

    # Act
    result = build_grid_system(trajectory_point_cloud, initialization_point)

    # Assert
    assert GridSystem == type(result)
    assert 20 == len(result.main_route)


def test_build_grid_system_empty_point_cloud():
    # Arrange
    initialization_point = (1, 1)
    point_cloud = TrajectoryPointCloud()

    # Act + Assert
    with pytest.raises(ValueError):
        build_grid_system(point_cloud, initialization_point)


def test_smooth_new_main_route_with_data():
    # Arrange
    main_route = {(1, 1)}
    smoothed_main_route = {(0, 1), (1, 1), (2, 1), (2, 2)}

    # Act
    (result_1, result_2) = smooth_new_main_route(
        main_route, smoothed_main_route)

    # Assert
    assert set == type(result_1)
    assert set == type(result_2)

    assert {(1.5, 1.5)} == result_1
    # Sorted as merging has no guaranteees of preserving the order.
    assert {(0, 1), (1, 1), (1.5, 1.5), (2, 1),
            (2, 2)} == set(sorted(result_2))


def test_smooth_new_main_route_with_no_data():
    # Arrange
    main_route = set()
    smoothed_main_route = set()

    # Act
    (result_1, result_2) = smooth_new_main_route(
        main_route, smoothed_main_route)

    # Assert
    assert set == type(result_1)
    assert set == type(result_2)

    assert set() == result_1
    assert set() == result_2


def test_smooth_new_main_route_with_no_new_data():
    # Arrange
    main_route = set()
    smoothed_main_route = {(0, 1), (1, 1), (2, 1), (2, 2)}

    # Act
    (result_1, result_2) = smooth_new_main_route(
        main_route, smoothed_main_route)

    # Assert
    assert set == type(result_1)
    assert set == type(result_2)

    assert set() == result_1
    assert smoothed_main_route == result_2  # No data, so no change.


def test_filter_smooth_main_route_no_filtering():
    # Arrange
    new_smooth_main_route = {(0, 1), (1, 1), (2, 1), (2, 2)}
    merged_smooth_main_route = {(0, 1), (1, 1), (2, 1), (2, 2)}
    min_pts = 1

    # Act
    result = filter_smoothed_main_route(
        merged_smooth_main_route, new_smooth_main_route, min_pts)

    # Assert
    # All points in merged are included, so all points should be returned.
    assert {(0, 1), (1, 1), (2, 1), (2, 2)} == result


def test_filter_smooth_main_route_return_whole_new_route():
    # Arrange
    new_smooth_main_route = {(1, 1), (2, 1)}
    merged_smooth_main_route = {(0, 1), (1, 1), (2, 1), (2, 2)}
    min_pts = 1

    # Act
    result = filter_smoothed_main_route(
        merged_smooth_main_route, new_smooth_main_route, min_pts)

    # Assert
    assert {(1, 1), (2, 1)} == result  # All points in merged are included.


def test_filter_smooth_main_route_return_partial_new_route():
    # Arrange
    new_smooth_main_route = {(1, 1), (2, 1), (30, 30)}
    merged_smooth_main_route = {(0, 1), (1, 1), (2, 1), (2, 2)}
    min_pts = 2

    # Act
    result = filter_smoothed_main_route(
        merged_smooth_main_route, new_smooth_main_route, min_pts)

    # Assert
    # (30, 30) should be filteres as an outlier
    assert {(1, 1), (2, 1)} == result


def test_update_safe_area():
    # Arrange
    initialization_point = (1, 1)
    old_smoothed_main_route = {(1, 1), (1, 1), (2, 1), (2, 2)}
    safe_area = SafeArea((10, -0.5), 10, 4, 0.1, 0.1, 0.1, 0.1)

    for i in range(100):
        point = Point(1 + 0.00001 * i, 1)
        safe_area.add_to_point_cloud(point)
    safe_areas = dict()
    safe_areas[safe_area.anchor] = safe_area

    # Act
    result = update_safe_area(safe_area, safe_areas,
                              initialization_point, old_smoothed_main_route)

    # Assert
    assert dict == type(result)
    assert (10, -0.5) == result[(10.0, -0.5)].anchor
