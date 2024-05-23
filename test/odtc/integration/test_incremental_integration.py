from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.noise_correction import NoiseCorrection
from DTC.json_read_write import read_set_of_tuples_from_json, read_point_cloud_from_json, read_safe_areas_from_json, read_grid_from_json
from math import ceil
from tqdm import tqdm
import pytest

@pytest.mark.skip
def test_safe_areas_can_be_updated():
    # Arrange
    data1 = read_point_cloud_from_json(
        "data/City area/1milcityPC.json")
    data2 = read_point_cloud_from_json(
        "data/City area/1milcityPC.json")
    test_data = data2.trajectories[:100]
    grid_system = GridSystem(data1)

    grid_system.grid_system = read_grid_from_json(
        "data/City area/1milcityGrid.json")
    grid_system.main_route = read_set_of_tuples_from_json(
        "data/City area/1milcityMR.json")

    route_skeleton = RouteSkeleton()
    smoothed_main_route = route_skeleton.smooth_main_route(
        grid_system.main_route, 25)
    filtered_main_route = route_skeleton.graph_based_filter(
        smoothed_main_route,
        20,
        ceil(len(grid_system.main_route) * 0.0001)
    )
    grid_system.route_skeleton = route_skeleton.filter_sparse_points(
        filtered_main_route,
        20
    )

    grid_system.safe_areas = read_safe_areas_from_json(
        "data/City area/1milcitySA.json", max_confidence_change=0.001)

    for trajectory in tqdm(test_data, desc="Cleaning trajectories"):
        cleaner = NoiseCorrection(
            grid_system.safe_areas, grid_system.initialization_point, smoothed_main_route)
        cleaner.noise_detection(trajectory)