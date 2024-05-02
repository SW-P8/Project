from DTC.trajectory import TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea, SafeArea

def update_safe_area(safe_area: SafeArea, safe_areas: dict, initialization_point, old_smoothed_main_route: set):
    safe_areas.pop(safe_area)
    point_cloud = create_trajectory_point_cloud(safe_area.get_point_cloud())

    grid_system = build_grid_system(point_cloud, initialization_point)
    
    new_smoothed_main_route, merged_smoothed_main_route = smooth_new_main_route(grid_system.main_route, old_smoothed_main_route)

    graphed_main_route = filter_smoothed_main_route(merged_smoothed_main_route, new_smoothed_main_route, len(old_smoothed_main_route))

    route_skeleton_ancors = RouteSkeleton.filter_sparse_points(graphed_main_route, 20) # 20 is the radius points cannot be within eachother.
    new_safe_areas = ConstructSafeArea.construct_safe_areas(route_skeleton_ancors, grid_system, 0.01, initialization_point) # 0.01 is the decrease factor used other places in the code base
    
    return new_safe_areas

def create_trajectory_point_cloud(start_trajectory):
    point_cloud = TrajectoryPointCloud()
    point_cloud.add_trajectory(start_trajectory)
    return point_cloud

def build_grid_system(point_cloud: TrajectoryPointCloud, initialization_point):
    grid_system = GridSystem(point_cloud)
    grid_system.create_grid_system(initialization_point)
    grid_system.extract_main_route()
    
    return grid_system

def smooth_new_main_route(main_route:set, smoothed_main_route: set):
    new_smoothed_main_route = RouteSkeleton.smooth_main_route(main_route, 20) # TODO: Why this number
    merged_smoothed_main_route = smoothed_main_route.union(new_smoothed_main_route)

    return new_smoothed_main_route, merged_smoothed_main_route

def filter_smoothed_main_route(merged_smoothed_main_route: set, new_smoothed_main_route: set, min_pts):
    graphed_main_route = RouteSkeleton.graph_based_filter(merged_smoothed_main_route, 20, min_pts)
    
    return graphed_main_route.intersection(set(new_smoothed_main_route))