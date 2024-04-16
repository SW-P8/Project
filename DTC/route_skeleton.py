from DTC.distance_calculator import DistanceCalculator
from collections import defaultdict
from typing import Iterator
import multiprocessing as mp
from DTC.collection_utils import CollectionUtils

class RouteSkeleton:
    @staticmethod
    def extract_route_skeleton(main_route: set, smooth_radius: int, filtering_list_radius: int, distance_interval: int):
        smoothed_main_route = RouteSkeleton.smooth_main_route(main_route, smooth_radius)
        contracted_main_route = RouteSkeleton.filter_outliers_in_smoothed_main_route(smoothed_main_route, len(main_route), filtering_list_radius)
        return RouteSkeleton.sample_contracted_main_route(contracted_main_route, distance_interval)

    @staticmethod
    def smooth_main_route(main_route: set, radius: int) -> defaultdict[set]:
        process_count = mp.cpu_count()
        splits =  CollectionUtils.split(main_route, process_count)
        tasks = []
        pipe_list = []

        for split in splits:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                task = mp.Process(target=RouteSkeleton.smooth_sub_main_route, args=(split, main_route, radius, send_end))
                tasks.append(task)
                pipe_list.append(recv_end)
                task.start()

        # Receive smoothed sub main routes from processes and merge
        smoothed_main_route = defaultdict(set)
        for (i, task) in enumerate(tasks):
            sub_smoothed_main_route = pipe_list[i].recv()
            task.join()
            for key, value in sub_smoothed_main_route.items():
                smoothed_main_route[key] = smoothed_main_route[key].union(value)

        return smoothed_main_route
    
    @staticmethod
    def smooth_sub_main_route(sub_main_route, main_route, radius, send_end):
        sub_smr = defaultdict(set)
        for (x1, y1) in sub_main_route:
            x_sum = 0
            y_sum = 0
            count = 0
            for i in range(x1 - radius, x1 + radius + 1):
                for j in range(y1 - radius, y1 + radius + 1):
                    if (i,j) in main_route and DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (i, j)) <= radius:
                        x_sum += i + 0.5
                        y_sum += j + 0.5
                        count += 1

            if x_sum != 0:
                x_sum /= count

            if y_sum != 0:
                y_sum /= count
            x_sum = round(x_sum, 2)
            y_sum = round(y_sum, 2)

            sub_smr[(int(x_sum), int(y_sum))].add((x_sum, y_sum))
        send_end.send(sub_smr)

    @staticmethod
    def filter_outliers_in_smoothed_main_route(smoothed_main_route: dict, main_route_length, radius_prime: int) -> defaultdict[set]:
        connection_threshold_factor = 0.01
        connection_threshold = connection_threshold_factor * main_route_length
        process_count = mp.cpu_count()
        splits =  CollectionUtils.split(smoothed_main_route.values(), process_count)
        tasks = []
        pipe_list = []

        for split in splits:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                task = mp.Process(target=RouteSkeleton.filter_outliers_in_sub_smoothed_main_route, args=(split, smoothed_main_route, connection_threshold, radius_prime, send_end))
                tasks.append(task)
                pipe_list.append(recv_end)
                task.start()

        # Receive filtered sub smoothed main routes from processes and merge
        contracted_main_route = defaultdict(set)
        for (i, task) in enumerate(tasks):
            sub_contracted_main_route = pipe_list[i].recv()
            task.join()
            for key, value in sub_contracted_main_route.items():
                contracted_main_route[key] = contracted_main_route[key].union(value)

        return contracted_main_route
        
    @staticmethod
    def filter_outliers_in_sub_smoothed_main_route(sub_smoothed_main_route: list, smoothed_main_route: dict, connection_threshold, radius_prime, send_end):
        sub_contracted_main_route = defaultdict(set)
        for cells in sub_smoothed_main_route:
            for (x1, y1) in cells:
                targets = 0
                for i in range(int(x1) - radius_prime, int(x1) + radius_prime + 1):
                    for j in range(int(y1) - radius_prime, int(y1) + radius_prime + 1):
                        candidates = smoothed_main_route.get((i, j))
                        if candidates is not None:
                            for (x2, y2) in candidates:
                                if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= radius_prime:
                                    targets += 1
                if targets >= connection_threshold:
                    sub_contracted_main_route[(int(x1), int(y1))].add((x1, y1))
        send_end.send(sub_contracted_main_route)
    
    @staticmethod
    def sample_contracted_main_route(contracted_main_route: dict, distance_interval: int) -> set:
        process_count = mp.cpu_count()
        splits =  CollectionUtils.split(contracted_main_route.values(), process_count)
        tasks = []
        pipe_list = []

        for split in splits:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                task = mp.Process(target=RouteSkeleton.sample_sub_contracted_main_route, args=(split, contracted_main_route, distance_interval, send_end))
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
    def sample_sub_contracted_main_route(sub_contracted_main_route, contracted_main_route, distance_interval, send_end):
        sub_route_skeleton = set()
        for cells in sub_contracted_main_route:
            for (x1, y1) in cells:
                targets = 0
                for i in range(int(x1) - distance_interval, int(x1) + distance_interval + 1):
                    for j in range(int(y1) - distance_interval, int(y1) + distance_interval + 1):
                        candidates = contracted_main_route.get((i, j))
                        if candidates is not None:
                            for (x2, y2) in candidates:
                                if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= distance_interval:
                                    targets += 1
                # targets should be greater than 1 to take self into account
                if targets > 1:
                    sub_route_skeleton.add((x1, y1))
        send_end.send(sub_route_skeleton)
     
