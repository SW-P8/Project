from DTC.gridsystem import GridSystem
from DTC.construct_main_route import ConstructMainRoute
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea, SafeArea
from scipy.spatial import KDTree

def update_safe_area(safe_area: SafeArea, safe_areas: KDTree):
    point_cloud = safe_area.get_point_cloud
    for neighbor in reverse_nearest_neigbor(safe_area.center, safe_areas):
        point_cloud = point_cloud.union(neighbor)
    pass

def reverse_nearest_neigbor(point, kd_tree: KDTree):
    nearest_neighbor_index = kd_tree.query([point], k=1)[1][0]

    points = kd_tree.data
    candidate_points = points[:nearest_neighbor_index] + points[:nearest_neighbor_index +1:]

    reverse_nearest_index = KDTree(candidate_points).query([points[nearest_neighbor_index]], k=1)[1][0]

    return points[nearest_neighbor_index], candidate_points[reverse_nearest_index]