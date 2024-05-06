from operator import itemgetter
from datetime import datetime
from math import sqrt, tanh
from DTC.distance_calculator import DistanceCalculator
import numpy as np
from collections import defaultdict
import multiprocessing as mp
from DTC.distance_calculator import DistanceCalculator
from DTC.collection_utils import CollectionUtils
from DTC.point import Point
from DTC.trajectory import Trajectory
from scipy.spatial import KDTree 

class ConstructSafeArea:
    @staticmethod
    def construct_safe_areas(route_skeleton: set, grid: dict, decrease_factor: float, find_relaxed_nn: bool = True) -> dict:
        cs = ConstructSafeArea._create_cover_sets(route_skeleton, grid, find_relaxed_nn)

        safe_areas = dict()

        for anchor in route_skeleton:
            safe_areas[anchor] = SafeArea.from_cover_set(cs[anchor], anchor, decrease_factor)

        return safe_areas

    @staticmethod
    def _create_cover_sets(route_skeleton: set, grid: dict, find_relaxed_nn: bool) -> dict:    
        process_count = mp.cpu_count()
        sub_grid_keys = CollectionUtils.split(grid.keys(), process_count)
        tasks = []
        pipe_list = []
        
        for split in sub_grid_keys:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                sub_grid = CollectionUtils.get_sub_dict_from_subset_of_keys(grid, split)
                task = mp.Process(target=ConstructSafeArea.create_cover_sets_sub_grid, args=(route_skeleton, sub_grid, find_relaxed_nn, send_end))
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
    def create_cover_sets_sub_grid(route_skeleton: set, grid: dict, find_relaxed_nn: bool, send_end):
        cs = defaultdict(set)
        route_skeleton_list = list(route_skeleton)
        route_skeleton_kd_tree = KDTree(route_skeleton_list)

        # Assign points to their nearest anchor
        if find_relaxed_nn:
            for (x, y) in grid.keys():
                candidates = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, (x + 0.5, y + 0.5))
                for point in grid[(x, y)]:
                    (anchor, dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(point, candidates, None)
                    cs[anchor].add((point, dist))
        else:
            for (x, y) in grid.keys():
                for point in grid[(x, y)]:
                    (anchor, dist) = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(point, route_skeleton_list, route_skeleton_kd_tree)
                    cs[anchor].add((point, dist))

        send_end.send(cs)

    @staticmethod
    def _find_candidate_nearest_neighbors(route_skeleton_list: list, route_skeleton_kd_tree: KDTree, cell: tuple) -> dict:
        distance_to_corner_of_cell = sqrt(0.5 ** 2 + 0.5 ** 2)        
        min_dist, _ = route_skeleton_kd_tree.query(cell)
        candidate_indices = route_skeleton_kd_tree.query_ball_point(cell, min_dist + distance_to_corner_of_cell)
        return [route_skeleton_list[i] for i in candidate_indices]
    
    @staticmethod
    def find_candidate_nearest_neighbors_with_historic_mindist(route_skeleton: set, cell: tuple) -> dict:
        historic_mindist = list()
        min_dist = float("inf")
        candidates = set()
        distance_to_corner_of_cell = sqrt(0.5 ** 2 + 0.5 ** 2)
        for anchor in route_skeleton:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells(cell, anchor)
            if dist <= min_dist + distance_to_corner_of_cell:
                if dist < min_dist:
                    min_dist = dist
                    historic_mindist.append(dist)
                candidates.add((anchor, dist))
        return ({a for a, d in candidates if d <= min_dist + distance_to_corner_of_cell}, historic_mindist)

class SafeArea:
    def __init__(self, anchor: tuple[float, float], radius: float, cardinality: int, confidence_change, normalisation_factor, cardinality_squish, max_confidence_change) -> None:
        """
        Initializes a SafeArea instance.

        Parameters:
            anchor (tuple[float, float]): The center point of the anchor area.
            radius (float) : The radius which in collaboration with the anchor makes up the safe area
            cardinality (int) : The amount of points contained in the cover set of the safe area
            confidence_change (float): The minimum change in confidence for each update.
            cardinality_normalisation (int): The normalization factor for cardinality in confidence calculations.
            cardinality_squish (float): The squishing factor for cardinality in confidence calculations.
            max_confidence_change (float): The maximum allowed change in confidence for each update. A value between 0 and 1.
            decrease_factor (float): The decrease a safe-area must see to have removed 'outliers'
        """
        self.anchor = anchor
        self.radius = radius
        self.cardinality = cardinality
        self.confidence = 1.0
        self.confidence_change_factor = confidence_change
        self.decay_factor = 1 / (60*60*24) # Set as the fraction of a day 1 second represents. Done as TimeDelta is given in seconds.
        self.timestamp =  None
        self.cardinality_normalisation = normalisation_factor
        self.cardinality_squish = cardinality_squish
        self.max_confidence_change = max_confidence_change
        

    def add_to_point_cloud(self, Point):
        self.PointsInSafeArea.append(Point)

    def get_point_cloud(self):
        return self.PointsInSafeArea

    def empty_point_cloud(self):
        self.PointsInSafeArea = []

    PointsInSafeArea = []

    @classmethod
    def from_cover_set(cls, cover_set: set, anchor: tuple[float, float], decrease_factor: float, confidence_change: float = 0.01, normalisation_factor: int = 100000, cardinality_squish: float = 0.1, max_confidence_change: float = 0.1):
        radius = SafeArea.calculate_radius(cover_set, decrease_factor)
        cardinality = len(cover_set)
        return cls(anchor, radius, cardinality, confidence_change, normalisation_factor, cardinality_squish, max_confidence_change)
    
    @classmethod
    def from_meta_data(cls, anchor: tuple[float, float], radius: float, cardinality: float, confidence_change: float = 0.01, normalisation_factor: int = 100000, cardinality_squish: float = 0.1, max_confidence_change: float = 0.1):
        return cls(anchor, radius, cardinality, confidence_change, normalisation_factor, cardinality_squish, max_confidence_change)

       
    @staticmethod   
    def calculate_radius(cover_set: set, decrease_factor: float):
        radius = max(cover_set, key=itemgetter(1), default=(0,0))[1]
        removed_count = 0
        cover_set_size = len(cover_set)
        removal_threshold = decrease_factor * cover_set_size
        filtered_cover_set = {(p, d) for (p, d) in cover_set}

        #Refine radius of safe area radius
        while removed_count < removal_threshold:
            radius *= (1 - decrease_factor)
            filtered_cover_set = {(p, d) for (p, d) in filtered_cover_set if d <= radius}
            removed_count = cover_set_size - len(filtered_cover_set)

        return radius

    def get_current_confidence(self, timestamp: datetime) -> tuple[float, datetime]:
        """
        Gets the current confidence and timestamp based on a given timestamp.

        Parameters:
            timestamp (datetime): The timestamp for calculating the current confidence.

        Returns:
            tuple[float, datetime]: The current confidence and timestamp.
        """
        delta = timestamp - self.timestamp
        new_confidence = self.confidence - self.calculate_time_decay(delta.total_seconds())
        return (new_confidence, timestamp)

    def set_confidence(self, confidence: float, timestamp: datetime):
        """
        Sets the confidence and timestamp of the SafeArea.

        Parameters:
            confidence (float): The new confidence value.
            timestamp (datetime): The timestamp associated with the confidence value.
        """
        self.confidence = confidence
        self.timestamp = timestamp

    def update_confidence(self, dist, point: Point):
        """
        Updates the confidence of the SafeArea based on the distance from a point.

        Parameters:
            dist (float): The distance from the SafeArea to the point.
            point (Point): The point used for updating the confidence.
        """
        distance_to_safearea = dist - self.radius 
        if (distance_to_safearea <= 0):
            (curr_conf, time) = self.get_current_confidence(point.timestamp)
            self.set_confidence(min(curr_conf + self.get_confidence_increase(), 1.0), time)
            self.cardinality += 1
        else:
            self.confidence -= self.calculate_confidence_decrease(distance_to_safearea)
    
    def calculate_time_decay(self, delta:float):
        """
        Calculates the time-based decay for confidence.

        Parameters:
            delta (float): The time difference in seconds.

        Returns:
            float: The decay factor for confidence.
        """
        decay = delta * self.decay_factor
        normalised_cardinality = self.cardinality / self.cardinality_normalisation
        cardinality_offset = self.sigmoid(normalised_cardinality, 3.0, -0.1, 1)
        decay = self.sigmoid(decay, -cardinality_offset, -0.5, 2) # -0.5 forces the line to go through (0,0) and 2 normalizes the function such that it maps any number to a value between -1 and 1
        decay = max(decay, 0.0)
        return round(decay, 5)
    
    
    def sigmoid(self, x: float, x_offset: float, y_offset, multiplier: float) -> float:
        return (1/(1 + np.exp((-x) + x_offset)) + y_offset) * multiplier

    def get_confidence_increase(self):
        inc = max(min((1 / (self.cardinality * self.cardinality_squish)), self.max_confidence_change), self.confidence_change_factor)
        return inc

    def calculate_confidence_decrease(self, delta):
        dec = 0.2*tanh((3*delta)/(4 * self.radius))
        return min(0.15, dec)
