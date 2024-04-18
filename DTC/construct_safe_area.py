from operator import itemgetter
from datetime import datetime
from math import sqrt, tanh, sinh
from DTC.distance_calculator import DistanceCalculator
import numpy as np
from collections import defaultdict

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
        
        cs = defaultdict(set)

        # Assign points to their nearest anchor
        for (x, y) in grid.keys():
            candidates = find_candidate_algorithm(route_skeleton, (x + 0.5, y + 0.5))
            for point in grid[(x, y)]:
                (anchor, dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(point, candidates, initialization_point)
                cs[anchor].add((point, dist))

        return cs

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

    def get_current_confidence_with_timestamp(self) -> tuple[float, datetime]:
        now = datetime.now()
        delta = now - self.timestamp
        new_confidence = self.confidence - self.__calculate_timed_decay(delta.total_seconds())
        return (new_confidence, now)

    def __set_confidence(self, confidence: float, timestamp: datetime):
        self.confidence = confidence
        self.timestamp = timestamp

    def update_confidence(self, dist):
        distance_to_sa = dist - self.radius 
        if (distance_to_sa <= 0):
            (curr_conf, time) = self.get_current_confidence_with_timestamp()
            self.__set_confidence(min(curr_conf + self.__get_confidence_increase(), 1.0), time)
            self.cardinality += 1
        else:
            self.confidence -= self.__calculate_confidence_decrease(distance_to_sa)
    
    def __calculate_timed_decay(self, delta:float):
        #More magic numbers because why not at this point?
        x = delta * self.__decay_factor
            
        print(f'delta = {delta}, cardinality = {self.cardinality}, x = {x}')
        cardinality_decay = min(SafeArea.sigmoid(self.cardinality, 1, 0, 0), 0.25)
        time_decay = SafeArea.sigmoid(x, 0, -0.5, 2)
        cardinality_decay = 0.0 # TODO: Implement impact of cardinality on decay
        total_decay = 1/2 * (time_decay + cardinality_decay)
        print(f"Timed decay = {time_decay}, Cardinality decay = {cardinality_decay}, Decay = {total_decay}")
        return round(total_decay, 5)
    
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
