""" Program entrypoint """
from DTC.dtc_executor import DTCExecutor
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from math import ceil


executor = DTCExecutor(True)
route_skeleton = RouteSkeleton()
point_cloud = executor.create_point_cloud_with_n_points(10000000, True, True)

grid_system = GridSystem(point_cloud)
grid_system.create_grid_system()
grid_system.extract_main_route()

min_pts = ceil(len(grid_system.main_route) * 0.0001)

smr = route_skeleton.smooth_main_route(grid_system.main_route, 20)
fmr = route_skeleton.graph_based_filter(smr, 15, min_pts)
grid_system.route_skeleton = route_skeleton.filter_sparse_points(fmr, 15)

grid_system.construct_safe_areas()
