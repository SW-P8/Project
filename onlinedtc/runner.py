from DTC.trajectory import TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.construct_main_route import ConstructMainRoute
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea, SafeArea
from scipy.spatial import KDTree

def update_safe_area(safe_area: SafeArea, safe_areas: KDTree, initialization_point, old_smooth_main_route):
    neighbor_set = reverse_nearest_neigbor(safe_area.center, safe_areas)
    point_cloud = create_trajectory_point_cloud(safe_area.get_point_cloud, neighbor_set)
    grid_system = GridSystem(point_cloud)
    grid_system.create_grid_system(initialization_point)
    grid_system.extract_main_route()
    smoothed_main_route = RouteSkeleton.smooth_main_route(grid_system.main_route, 20)
    while check_overlap_for_main_routes(old_smooth_main_route, smoothed_main_route) < 50: # TODO: This needs to be checked differently, perhaps if possible do a scan of the area around the neighborset??? idk
        iteration = 2
        neighbor_set = reverse_nearest_neigbor(safe_area, safe_areas, iteration)
        point_cloud = TrajectoryPointCloud()
        point_cloud.add_trajectory(safe_area.get_point_cloud())
        for neighbor in neighbor_set:
            point_cloud.add_trajectory(neighbor.get_point_cloud())
        grid_system = GridSystem(point_cloud)
        grid_system.create_grid_system(initialization_point)
        smoothed_main_route = RouteSkeleton.smooth_main_route(grid_system.main_route, 20)
    



    pass


def reverse_nearest_neigbor(point, kd_tree: KDTree, n: int = 1):
    nearest_neighbor_index = kd_tree.query([point], k=1)[1][0]

    points = kd_tree.data
    candidate_points = points[:nearest_neighbor_index] + points[:nearest_neighbor_index +1:]

    reverse_nearest_index = KDTree(candidate_points).query([points[nearest_neighbor_index]], k=n)[1][0]

    return points[nearest_neighbor_index], candidate_points[reverse_nearest_index]

def check_overlap_for_main_routes(original_main_route: set, new_main_route: set):
    if original_main_route == set() or new_main_route == set():
        return 0
    
    overlap = original_main_route.intersection(new_main_route)
    return (len(overlap) / len(new_main_route)) * 100

def create_trajectory_point_cloud(start_trajectory, neighbor_set):
    point_cloud = TrajectoryPointCloud()
    point_cloud.add_trajectory(start_trajectory)
    for neighbor in neighbor_set:
        point_cloud.add_trajectory(neighbor.get_point_cloud())
    return point_cloud