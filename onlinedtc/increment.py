from DTC.trajectory import TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea, SafeArea
from math import ceil
import config


def update_safe_area(safe_areas: dict[SafeArea], initialization_point, old_smoothed_main_route: set):
    point_cloud = create_trajectory_point_cloud(safe_areas)
    grid_system = build_grid_system(point_cloud, initialization_point)

    new_smoothed_main_route, merged_smoothed_main_route = smooth_new_main_route(
        grid_system.main_route, old_smoothed_main_route)

    min_pts = ceil(len(old_smoothed_main_route) * config.min_pts_from_mr)

    old_smoothed_main_route = merged_smoothed_main_route

    graphed_main_route = filter_smoothed_main_route(
        merged_smoothed_main_route, new_smoothed_main_route, min_pts)

    # Check if any anchors remain. If not return empty.
    if len(graphed_main_route) == 0:
        return dict()

    # 20 is the radius points cannot be within eachother.
    route_skeleton_ancors = RouteSkeleton.filter_sparse_points(
        graphed_main_route, config.distance_interval)
    # 0.01 is the decrease factor used other places in the code base
    new_safe_areas = ConstructSafeArea.construct_safe_areas(
        route_skeleton_ancors, grid_system.grid, config.decrease_factor, initialization_point)
    for safe_area in new_safe_areas.values():
        safe_area.timestamp = grid_system.max_timestamp

    return new_safe_areas


def create_trajectory_point_cloud(safe_areas: dict[SafeArea]):
    point_cloud = TrajectoryPointCloud()
    for safe_area in safe_areas.values():
        point_cloud.add_trajectory(safe_area.get_point_cloud())

    return point_cloud


def build_grid_system(point_cloud: TrajectoryPointCloud, initialization_point):
    grid_system = GridSystem(point_cloud)
    grid_system.initialization_point = initialization_point
    grid_system.create_grid_system()
    grid_system.extract_main_route()

    return grid_system


def smooth_new_main_route(main_route: set, smoothed_main_route: set):
    new_smoothed_main_route = RouteSkeleton.smooth_main_route(
        main_route, config.smooth_radius)
    merged_smoothed_main_route = smoothed_main_route.union(
        new_smoothed_main_route)

    return new_smoothed_main_route, merged_smoothed_main_route


def filter_smoothed_main_route(merged_smoothed_main_route: set, new_smoothed_main_route: set, min_pts):
    graphed_main_route = RouteSkeleton.graph_based_filter(
        merged_smoothed_main_route, config.filtering_list_radius, min_pts)

    return graphed_main_route.intersection(set(new_smoothed_main_route))
