from DTC.distance_calculator import DistanceCalculator
from collections import defaultdict
from typing import Iterator
import multiprocessing as mp
from math import dist, floor
from DTC.collection_utils import CollectionUtils
from copy import deepcopy

class RouteSkeleton:
    @staticmethod
    def extract_route_skeleton(main_route: set, smooth_radius: int, filtering_list_radius: int, distance_interval: int):
        smoothed_main_route = RouteSkeleton.smooth_main_route(main_route, smooth_radius)
        contracted_main_route = RouteSkeleton.filter_outliers_in_smoothed_main_route(smoothed_main_route, len(main_route), filtering_list_radius)
        return RouteSkeleton.sample_contracted_main_route(contracted_main_route, distance_interval)

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

    def graph_based_filter(data: set, epsilon: float, min_pts) -> set:
        visited = set()
        clusters = set()
        
        def expand_cluster(point: tuple, cluster: set, visited):
            cluster.add(point)
            visited.add(point)
            neighbors = {p for p in data if p not in visited and DistanceCalculator.calculate_euclidian_distance_between_cells(point, p) <= epsilon}
            for neighbor in neighbors:
                expand_cluster(neighbor, cluster, visited)
        
        for point in data:
            if point not in visited:
                cluster = set()
                expand_cluster(point, cluster, visited)
                if len(cluster) >= min_pts:
                    clusters = clusters.union(cluster)
        
        return clusters
    
    def filter_sparse_points(data: set, distance_threshold):
        points = deepcopy(data)
        filtered_points = set()
        for point1 in points:
            if point1 not in filtered_points:
                for point2 in points:
                    if point1 != point2 and DistanceCalculator.calculate_euclidian_distance_between_cells(point1, point2) < distance_threshold:
                        filtered_points.add(point2)
        points.difference_update(filtered_points)
        return points

    @staticmethod
    def sample_contracted_main_route(contracted_main_route: dict, distance_interval: int) -> set:
        process_count = mp.cpu_count()
        sorted_contracted_main_route_keys = CollectionUtils.sort_collection_of_tuples(contracted_main_route.keys())
        sub_contracted_main_route_keys_list =  CollectionUtils.split(sorted_contracted_main_route_keys, process_count)
        tasks = []
        pipe_list = []

        for sub_contracted_main_route_keys in sub_contracted_main_route_keys_list:
            if sub_contracted_main_route_keys != []:
                recv_end, send_end = mp.Pipe(False)
                bounds = CollectionUtils.get_min_max_with_padding_from_collection_of_tuples(sub_contracted_main_route_keys, distance_interval)
                sub_contracted_main_route_with_padding_keys = CollectionUtils.get_tuples_within_bounds(sorted_contracted_main_route_keys, bounds)
                sub_contracted_main_route_with_padding_dict = CollectionUtils.get_sub_dict_from_subset_of_keys(contracted_main_route, sub_contracted_main_route_with_padding_keys)
                task = mp.Process(target=RouteSkeleton.sample_sub_contracted_main_route, args=(sub_contracted_main_route_keys, sub_contracted_main_route_with_padding_dict, distance_interval, send_end))
                tasks.append(task)
                pipe_list.append(recv_end)
                task.start()

        # Receive sampled sub contracted main routes from processes and merge
        route_skeleton = set()
        for (i, task) in enumerate(tasks):
            sub_route_skeleton = pipe_list[i].recv()
            task.join()
            route_skeleton = route_skeleton.union(sub_route_skeleton)

        return route_skeleton
        
    @staticmethod
    def sample_sub_contracted_main_route(sub_contracted_main_route_keys: set, sub_contracted_main_route_with_padding, distance_interval: int, send_end):
        sub_route_skeleton = set()
        for key in sub_contracted_main_route_keys:
            for (x1, y1) in sub_contracted_main_route_with_padding[key]:
                targets = 0
                for i in range(int(x1) - distance_interval, int(x1) + distance_interval + 1):
                    for j in range(int(y1) - distance_interval, int(y1) + distance_interval + 1):
                        candidates = sub_contracted_main_route_with_padding.get((i, j))
                        if candidates is not None:
                            for (x2, y2) in candidates:
                                if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= distance_interval:
                                    targets += 1
                # targets should be greater than 1 to take self into account
                if targets > 1:
                    sub_route_skeleton.add((x1, y1))
        send_end.send(sub_route_skeleton)
     
