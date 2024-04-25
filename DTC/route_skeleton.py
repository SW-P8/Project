from operator import itemgetter
from DTC.distance_calculator import DistanceCalculator
from collections import defaultdict
import multiprocessing as mp
from math import ceil
from DTC.collection_utils import CollectionUtils
from copy import deepcopy
from sklearn.cluster import DBSCAN
from concurrent.futures import ThreadPoolExecutor
import threading
from scipy.spatial import KDTree
import numpy as np

class RouteSkeleton:
    @staticmethod
    def extract_route_skeleton(main_route: set, smooth_radius: int, filtering_list_radius: int, distance_interval: int):
        min_pts = ceil(0.01 * len(main_route))
        smoothed_main_route = RouteSkeleton.smooth_main_route(main_route, smooth_radius)
        contracted_main_route = RouteSkeleton.graph_based_filter(smoothed_main_route, filtering_list_radius, min_pts)
        return RouteSkeleton.filter_sparse_points(contracted_main_route, distance_interval)

    @staticmethod
    def smooth_main_route(main_route: set, radius: int) -> defaultdict[set]:
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
        sub_smoothed_main_route = set()
        for (x1, y1) in sub_main_route:
            x_sum = 0
            y_sum = 0
            count = 0
            for i in range(x1 - radius, x1 + radius + 1):
                for j in range(y1 - radius, y1 + radius + 1):
                    if (i,j) in sub_main_route_with_padding and DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (i, j)) <= radius:
                        x_sum += i + 0.5
                        y_sum += j + 0.5
                        count += 1

            if x_sum != 0:
                x_sum /= count

            if y_sum != 0:
                y_sum /= count
            x_sum = round(x_sum, 2)
            y_sum = round(y_sum, 2)

            sub_smoothed_main_route.add((x_sum, y_sum))
        send_end.send(sub_smoothed_main_route)

    @staticmethod
    def graph_based_filter(data: set, epsilon: float, min_pts) -> set:
        main_route = np.array(list(data))
        dbscan = DBSCAN(eps=epsilon, min_samples=min_pts, metric="euclidean")
        dbscan.fit(main_route)
        filtered_main_route = main_route[dbscan.labels_ != -1].T
        return set(zip(filtered_main_route[0], filtered_main_route[1]))

    @staticmethod
    def filter_sparse_points(data: set, distance_threshold):
        points = deepcopy(data)
        pp = PointProcessor(points, distance_threshold)
        sampled_set = set()
        pp.process_points()
        sparse_points = pp.get_sparse_points()
        #while points != []:
        #    source = points[0]
        #    sampled_set.add(source)
        #    points.remove(source)
        #    for target in points:
        #        if (source[0] - target[0])**2 + (source[1] - target[1])**2 < distance_threshold**2:
        #            points.remove(target)


        #for source in points:
        #    if source not in filtered_points:
        #        for target in points:
        #            if source != target and  (source[0] - target[0])**2 + (source[1] - target[1])**2 < distance_threshold**2:
        #                   filtered_points.add(target)
        #    points.difference_update(filtered_points)
        return sparse_points



class PointProcessor:
    def __init__(self, data, distance_threshold):
        self.points = list(deepcopy(data))
        self.distance_threshold = distance_threshold
        self.filtered_points = set()
        self.kd_tree = KDTree(self.points)

    def process_points(self):
        to_remove = set()  # Track points to remove
        for source in self.points:
            if source not in self.filtered_points:
                indices = self.kd_tree.query_ball_point(source, self.distance_threshold - 0.01)
                local_filtered = {tuple(self.points[i]) for i in indices if self.points[i] != source}
                self.filtered_points.update(local_filtered)
                to_remove.update(local_filtered)
        # Update the points list by removing filtered points
        self.points = [point for point in self.points if tuple(point) not in to_remove]

    def get_sparse_points(self):
        # Since self.points has already been filtered, just return it
        return set(self.points)


# Example usage:
