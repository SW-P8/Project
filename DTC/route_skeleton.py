from collections import defaultdict
from math import ceil
from copy import deepcopy
from sklearn.cluster import DBSCAN
from scipy.spatial import KDTree
import numpy as np
import multiprocessing as mp
from DTC.collection_utils import CollectionUtils

import config

class RouteSkeleton:
    @staticmethod
    def extract_route_skeleton(main_route: set, smooth_radius: int=config.smooth_radius, filtering_list_radius: int = config.filtering_list_radius, distance_interval: int = config.distance_interval):
        min_pts = ceil(0.0001 * len(main_route))
        smoothed_main_route = RouteSkeleton.smooth_main_route(main_route, smooth_radius)
        contracted_main_route = RouteSkeleton.graph_based_filter(smoothed_main_route, filtering_list_radius, min_pts)
        return RouteSkeleton.filter_sparse_points(contracted_main_route, distance_interval)

    @staticmethod
    def smooth_main_route(main_route: set, radius: int = config.smooth_radius) -> defaultdict[set]:
        process_count = mp.cpu_count()
        sorted_main_route = CollectionUtils.sort_collection_of_tuples(main_route)
        sub_main_routes =  CollectionUtils.split(sorted_main_route, process_count)
        tasks = []
        pipe_list = []

        for sub_main_route in sub_main_routes:
            if sub_main_route != []:
                recv_end, send_end = mp.Pipe(False)
                bounds = CollectionUtils.get_min_max_with_padding_from_collection_of_tuples(sub_main_route, radius)
                sub_main_route_with_padding = CollectionUtils.get_tuples_within_bounds(sorted_main_route, bounds)
                task = mp.Process(target=RouteSkeleton.smooth_sub_main_route, args=(sub_main_route, sub_main_route_with_padding, radius, send_end))
                tasks.append(task)
                pipe_list.append(recv_end)
                task.start()

        # Receive smoothed sub main routes from processes and merge
        smoothed_main_route = set()
        for (i, task) in enumerate(tasks):
            sub_smoothed_main_route = pipe_list[i].recv()
            task.join()
            smoothed_main_route = smoothed_main_route.union(sub_smoothed_main_route)
        
        return smoothed_main_route
    
    @staticmethod
    def smooth_sub_main_route(sub_main_route: set, sub_main_route_with_padding: set, radius: int, send_end):
        cell_centers = [(x + 0.5, y + 0.5) for (x,y) in sub_main_route]
        cell_centers_with_padding = [(x + 0.5, y + 0.5) for (x,y) in sub_main_route_with_padding]
        kd_tree = KDTree(cell_centers_with_padding)
        sub_smoothed_main_route = set()
        
        for cell_center in cell_centers:
            indices = kd_tree.query_ball_point(cell_center, radius)
            neighbour_set = {tuple(cell_centers_with_padding[i]) for i in indices}
            avg_point = tuple(round(sum(x)/len(x), 2) for x in zip(*neighbour_set))
            sub_smoothed_main_route.add(avg_point)

        send_end.send(sub_smoothed_main_route)

    @staticmethod
    def graph_based_filter(data: set, epsilon: float = config.filtering_list_radius, min_pts: int = 0) -> set:
        main_route = np.array(list(data))
        dbscan = DBSCAN(eps=epsilon, min_samples=min_pts, metric="euclidean")
        dbscan.fit(main_route)
        filtered_main_route = main_route[dbscan.labels_ != -1].T
        return set(zip(filtered_main_route[0], filtered_main_route[1]))

    @staticmethod
    def filter_sparse_points(data: set, distance_threshold: float = config.distance_interval):
        points = list(deepcopy(data))
        kd_tree = KDTree(points)
        filtered_points = set() # Track points to remove

        for source in points:
            if source not in filtered_points:
                indices = kd_tree.query_ball_point(source, distance_threshold - 0.01)
                local_filtered = {tuple(points[i]) for i in indices if points[i] != source}
                filtered_points.update(local_filtered)

        # Update the points list by removing filtered points
        return {point for point in points if tuple(point) not in filtered_points}
