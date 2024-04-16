from DTC.distance_calculator import DistanceCalculator
from collections import defaultdict
from typing import Iterator
import multiprocessing as mp

class RouteSkeleton:
    @staticmethod
    def extract_route_skeleton(main_route: set, smooth_radius: int, filtering_list_radius: int, distance_interval: int):
        smr = RouteSkeleton.smooth_main_route(main_route, smooth_radius)
        cmr = RouteSkeleton.filter_outliers_in_main_route(smr, len(main_route), filtering_list_radius)
        return RouteSkeleton.sample_main_route(cmr, distance_interval)

    @staticmethod
    def smooth_main_route(main_route: set, radius: int, multiprocessing: bool = True) -> set:
        if(multiprocessing):
            process_count = mp.cpu_count()
            splits = RouteSkeleton.split(main_route, process_count)
            tasks = []
            pipe_list = []

            for split in splits:
                if split != []:
                    recv_end, send_end = mp.Pipe(False)
                    t = mp.Process(target=RouteSkeleton.smooth_sub_main_route, args=(split, main_route, radius, send_end))
                    tasks.append(t)
                    pipe_list.append(recv_end)
                    t.start()

            # Receive subgrids from processes and merge
            merged_dict = defaultdict(set)
            for (i, task) in enumerate(tasks):
                d = pipe_list[i].recv()
                task.join()
                for key, value in d.items():
                    merged_dict[key] = merged_dict[key].union(value)

            return merged_dict
        else:
            smr  = defaultdict(set)
            for (x1, y1) in main_route:
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

                smr[(int(x_sum), int(y_sum))].add((x_sum, y_sum))
            return smr
    
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
    def split(a, n) -> Iterator[set]:
        a = list(a)
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    @staticmethod
    def filter_outliers_in_main_route(smr: dict, main_route_length, radius_prime: int) -> set:
        cmr = defaultdict(set)
        connection_threshold_factor = 0.01
        connection_threshold = connection_threshold_factor * main_route_length
        for cell_values in smr.values():
            for (x1, y1) in cell_values:
                targets = 0
                for i in range(int(x1) - radius_prime, int(x1) + radius_prime + 1):
                    for j in range(int(y1) - radius_prime, int(y1) + radius_prime + 1):
                        candidates = smr.get((i, j))
                        if candidates is not None:
                            for (x2, y2) in candidates:
                                if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= radius_prime:
                                    targets += 1
                if targets >= connection_threshold:
                    cmr[(int(x1), int(y1))].add((x1, y1))
        return cmr
    
    @staticmethod
    def sample_main_route(cmr: dict, distance_interval: int) -> set:
        rs = set()
        for cell_values in cmr.values():
            for (x1, y1) in cell_values:
                targets = 0
                for i in range(int(x1) - distance_interval, int(x1) + distance_interval + 1):
                    for j in range(int(y1) - distance_interval, int(y1) + distance_interval + 1):
                        candidates = cmr.get((i, j))
                        if candidates is not None:
                            for (x2, y2) in candidates:
                                if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= distance_interval:
                                    targets += 1
                # targets should be greater than 1 to take self into account
                if targets > 1:
                    rs.add((x1, y1))
        return rs
     
