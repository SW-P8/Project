from DTC.trajectory import TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea, SafeArea
import config


def update_safe_area(safe_areas: dict[SafeArea], initialization_point):
    point_cloud = create_trajectory_point_cloud(safe_areas)
    grid_system = build_grid_system(point_cloud, initialization_point)

    smoothed_main_route = RouteSkeleton.smooth_main_route(
        grid_system.main_route, config.smooth_radius)

    if smoothed_main_route is None or len(smoothed_main_route) == 0:
        return dict()

    route_skeleton_anchors = RouteSkeleton.filter_sparse_points(
        smoothed_main_route, config.distance_interval)

    new_safe_areas = ConstructSafeArea.construct_safe_areas(
        route_skeleton_anchors, grid_system.grid, config.decrease_factor, initialization_point, grid_system.max_timestamp)

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
