from DTC.clean_trajectory import CleanTrajectory
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.dtc_executor import DTCExecutor
from math import ceil
from tqdm import tqdm
import pytest


@pytest.fixture
def data():
    executor = DTCExecutor(True)
    return executor.create_point_cloud_with_n_points(300000, True, True)


@pytest.fixture
def model_data(data):
    point_cloud = data
    point_cloud.trajectories = data.trajectories[:1000]
    return point_cloud


@pytest.fixture
def testing_data(data):
    testing_data = data.trajectories[1000:1050]
    return testing_data


@pytest.fixture
def model(model_data):
    grid_system = GridSystem(model_data)
    route_skeleton = RouteSkeleton()

    grid_system.create_grid_system()

    grid_system.extract_main_route()

    min_pts_in_component = ceil(len(grid_system.main_route) * 0.0001)

    smoothed_main_route = route_skeleton.smooth_main_route(
        grid_system.main_route, 25)
    filtered_main_route = route_skeleton.graph_based_filter(
        smoothed_main_route, 20, min_pts_in_component)
    grid_system.route_skeleton = route_skeleton.filter_sparse_points(
        filtered_main_route, 20)

    grid_system.construct_safe_areas()
    return grid_system, smoothed_main_route


@pytest.fixture
def cleaner(model):
    grid_system, _ = model
    cleaner = CleanTrajectory(
        grid_system.safe_areas,
        grid_system.route_skeleton,
        grid_system.initialization_point)
    return cleaner


@pytest.mark.skip
def test_safe_areas_can_be_updated(model, cleaner, testing_data):
    grid_system, smoothed_main_route = model
    for trajectory in tqdm(testing_data, desc="Cleaning trajectories"):
        cleaner.clean(trajectory)
    pass
