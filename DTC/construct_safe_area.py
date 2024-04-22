from operator import itemgetter
from datetime import datetime
from math import sqrt, tanh, sinh
from DTC.distance_calculator import DistanceCalculator
import numpy as np

from collections import defaultdict
import multiprocessing as mp
from DTC.distance_calculator import DistanceCalculator
from DTC.collection_utils import CollectionUtils
from DTC.point import Point

class ConstructSafeArea:
    @staticmethod
    def construct_safe_areas(route_skeleton: set, grid: dict, decrease_factor: float, initialization_point) -> dict:
        cs = ConstructSafeArea._create_cover_sets(route_skeleton, grid, initialization_point)

        safe_areas = dict()

        for anchor in route_skeleton:
            safe_areas[anchor] = SafeArea(cs[anchor], anchor, decrease_factor)

        return safe_areas

    @staticmethod
    def _create_cover_sets(route_skeleton: set, grid: dict, initialization_point: tuple, find_candidate_algorithm = None) -> dict:
        if find_candidate_algorithm is None:
            find_candidate_algorithm = ConstructSafeArea._find_candidate_nearest_neighbors
        
        process_count = mp.cpu_count()
        sub_grid_keys = CollectionUtils.split(grid.keys(), process_count)
        tasks = []
        pipe_list = []
        
        for split in sub_grid_keys:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                sub_grid = CollectionUtils.get_sub_dict_from_subset_of_keys(grid, split)
                task = mp.Process(target=ConstructSafeArea.create_cover_sets_sub_grid, args=(route_skeleton, sub_grid, initialization_point, find_candidate_algorithm, send_end))
                tasks.append(task)
                pipe_list.append(recv_end)
                task.start()

        # Receive subgrids from processes and merge
        merged_dict = defaultdict(set)
        for (i, task) in enumerate(tasks):
            d = pipe_list[i].recv()
            task.join()
            for key, value in d.items():
                merged_dict[key] = merged_dict[key].union(value)

        return merged_dict

    @staticmethod
    def create_cover_sets_sub_grid(route_skeleton: set, grid: dict, initialization_point: tuple, find_candidate_algorithm, send_end):
        cs = defaultdict(set)

        # Assign points to their nearest anchor
        for (x, y) in grid.keys():
            candidates = find_candidate_algorithm(route_skeleton, (x + 0.5, y + 0.5))
            for point in grid[(x, y)]:
                (anchor, dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(point, candidates, initialization_point)
                cs[anchor].add((point, dist))

        send_end.send(cs)

    @staticmethod
    def _find_candidate_nearest_neighbors(route_skeleton: set, cell: tuple) -> dict:
        min_dist = float("inf")
        candidates = set()
        distance_to_corner_of_cell = sqrt(0.5 ** 2 + 0.5 ** 2)
        
        for anchor in route_skeleton:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells(cell, anchor)
            if dist <= min_dist + distance_to_corner_of_cell:
                if dist < min_dist:
                    min_dist = dist
                candidates.add((anchor, dist))

        return {a for a, d in candidates if d <= min_dist + distance_to_corner_of_cell}

class SafeArea:
    def __init__(self, anchor_cover_set, anchor: tuple[float, float], decrease_factor: float, confidence_change: float = 0.01, squish_factor: float = 0.5) -> None:
        self.center = anchor
        self.radius = 0
        self.cardinality = 0
        self.confidence = 1.0
        self.__confidence_change_factor = confidence_change
        self.__decay_factor = 1 / (60*60*24)
        self.__squish_factor = squish_factor
        self.timestamp: datetime = datetime.now() # Could be used to indicate creation or update time if we use time for weights, change value.
        self.construct(anchor_cover_set, decrease_factor)

    def construct(self, anchor, decrease_factor):
        self.calculate_radius(anchor, decrease_factor)
       
    def calculate_radius(self, anchor, decrease_factor: float = 0.01):
        radius = max(anchor, key=itemgetter(1), default=(0,0))[1]
        removed_count = 0
        cover_set_size = len(anchor)
        removal_threshold = decrease_factor * cover_set_size
        filtered_cover_set = {(p, d) for (p, d) in anchor}

        #Refine radius of safe area radius
        while removed_count < removal_threshold:
            radius *= (1 - decrease_factor)
            filtered_cover_set = {(p, d) for (p, d) in filtered_cover_set if d <= radius}
            removed_count = cover_set_size - len(filtered_cover_set)

        self.cardinality = len(filtered_cover_set)
        self.radius = radius

    def get_current_confidence_with_timestamp(self, timestamp_from_point: datetime) -> tuple[float, datetime]:
        now = timestamp_from_point
        delta = now - self.timestamp
        new_confidence = self.confidence - self.__calculate_timed_decay(delta.total_seconds())
        return (new_confidence, now)

    def __set_confidence(self, confidence: float, timestamp: datetime):
        self.confidence = confidence
        self.timestamp = timestamp

    def update_confidence(self, dist, point: Point):
        distance_to_sa = dist - self.radius 
        if (distance_to_sa <= 0):
            (curr_conf, time) = self.get_current_confidence_with_timestamp(point.timestamp)
            self.__set_confidence(min(curr_conf + self.__get_confidence_increase(), 1.0), time)
            self.cardinality += 1
        else:
            self.confidence -= self.__calculate_confidence_decrease(distance_to_sa)
    
    def __calculate_timed_decay(self, delta:float):
        #More magic numbers because why not at this point?
        x = delta * self.__decay_factor
        normalised_cardinality = self.cardinality / 100000
        cardinality_offset = SafeArea.sigmoid(normalised_cardinality, 3.0, -0.1, 1)    # Division by 100000 and the number 3 are just magic numbers lmao
        print(f'delta = {delta}, cardinality = {self.cardinality}, x = {x}, Cardinality offset = {cardinality_offset}')
        decay = SafeArea.sigmoid(x, -cardinality_offset, -0.5, 2) # -0.5 forces the line to go through (0,0) and 2 normalizes the function such that it maps any number to a value between -1 and 1
        print(f"Timed decay = {decay}")
        decay = max(decay, 0.0)
        return round(decay, 5)
    
    @staticmethod
    def sigmoid(x: float, x_offset: float, y_offset, multiplier: float) -> float:
        return (1/(1 + np.exp((-x) + x_offset)) + y_offset) * multiplier

    def __get_confidence_increase(self):
        inc = max(min((1 / (self.cardinality * 1/10)), 0.1), self.__confidence_change_factor)
        print(f'increase = {inc}')
        return inc

    def __calculate_confidence_decrease(self, delta):
        dec = 0.2*tanh((3*delta)/(4 * self.radius))
        return min(0.15, dec)
