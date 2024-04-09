from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator
from math import floor, sqrt
from operator import itemgetter
from datetime import datetime
from typing import Optional
from progress.counter import Counter
from route_skeleton import RouteSkeletonWrapper

class GridSystem:
    def __init__(self, pc: TrajectoryPointCloud) -> None:
        self.pc = pc
        self.initialization_point = pc.get_shifted_min()
        self.cell_size = pc.cell_size
        self.neighborhood_size = pc.neighborhood_size
        self.grid = dict()
        self.populated_cells = set()
        self.main_route = set()
        self.route_skeleton = set()
        self.safe_areas = dict()


    def create_grid_system(self):
        # Fill grid with points
        count = Counter('Creating Grid System - Elapsed: %(elapsed)ds  Count: ')
        for trajectory in self.pc.trajectories:
            for point in trajectory.points:
                count.next()
                (x,y) = self.calculate_exact_index_for_point(point)
                floored_index = (floor(x), floor(y))
                if floored_index not in self.populated_cells:
                    self.populated_cells.add(floored_index)
                    self.grid[floored_index] = list()
                self.grid[floored_index].append(point)
        count.finish()

    def calculate_exact_index_for_point(self, point: Point):
        # Calculate x index
        x_offset = DistanceCalculator.get_distance_between_points(self.initialization_point, (point.longitude, self.initialization_point[1]))
        x_coordinate = (x_offset / self.cell_size) - 1

        # Calculate y index
        y_offset = DistanceCalculator.get_distance_between_points(self.initialization_point, (self.initialization_point[0], point.latitude))
        y_coordinate = (y_offset / self.cell_size) - 1

        return (x_coordinate, y_coordinate)
    
    def extract_main_route(self, distance_scale: float = 0.2):
        if distance_scale >= 0.5:
            raise ValueError("distance scale must be less than neighborhood size divided by 2")
        distance_threshold = distance_scale * self.neighborhood_size

        count = Counter('Extracting main route - Elapsed: %(elapsed)ds  Count: ')
        for cell in self.populated_cells:
            density_center = self.calculate_density_center(cell)

            if DistanceCalculator.calculate_euclidian_distance_between_cells(cell, density_center) < distance_threshold:
                self.main_route.add(cell)

    def calculate_density_center(self, index):
        (x, y) = index
        l = self.neighborhood_size // 2
        point_count = 0
        (x_sum, y_sum) = (0, 0)
 
        for i in range(x - l, x + l + 1):
            for j in range(y - l, y + l + 1):
                if (i, j) in self.populated_cells:
                    cardinality = len(self.grid[(i, j)])
                    x_sum += cardinality * i
                    y_sum += cardinality * j
                    point_count += cardinality

        if x_sum != 0:
            x_sum /= point_count

        if y_sum != 0:
            y_sum /= point_count

        return (x_sum, y_sum)
    
    def extract_route_skeleton(self, smooth_radius: int = 25, filtering_list_radius: int = 20, distance_interval: int = 20):
        rsw = RouteSkeletonWrapper(self.main_route)
        rsw.extract_route_skeleton()
    
    def construct_safe_areas(self, decrease_factor: float = 0.01):
        cs = self.create_cover_sets()
        count = Counter('Constructing Safe Areas - Elapsed: %(elapsed)ds  Count: ')
        for anchor in self.route_skeleton:
            count.next()
            #Initialize safe area radius
            radius = max(cs[anchor], key=itemgetter(1), default=(0,0))[1]
            removed_count = 0
            cs_size = len(cs[anchor])
            removal_threshold = decrease_factor * cs_size
            filtered_cs = {(p, d) for (p, d) in cs[anchor]}

            #Refine radius of safe area radius
            while removed_count < removal_threshold:
                radius *= (1 - decrease_factor)
                filtered_cs = {(p, d) for (p, d) in filtered_cs if d <= radius}
                removed_count = cs_size - len(filtered_cs)

            self.safe_areas[anchor] = radius
        count.finish()
    
    def create_cover_sets(self, find_candidate_algorithm = None):
        if find_candidate_algorithm is None:
            find_candidate_algorithm = self.find_candidate_nearest_neighbors
        cs = dict()
        count = Counter('Creating cover sets - Elapsed: %(elapsed)ds  Count: ')
        # Initialize dictionary with a key for each anchor and an empty set for each
        for anchor in self.route_skeleton:
            count.next()
            cs[anchor] = set()

        # Assign points to their nearest anchor
        for (x, y) in self.populated_cells:
            candidates = find_candidate_algorithm((x + 0.5, y + 0.5))
            for point in self.grid[(x, y)]:
                count.next()
                (anchor, dist) = self.find_nearest_neighbor_from_candidates(point, candidates)
                cs[anchor].add((point, dist))
        count.finish()
        return cs


    def find_candidate_nearest_neighbors(self, cell):
        min_dist = float("inf")
        candidates = set()
        distance_to_corner_of_cell = sqrt(0.5 ** 2 + 0.5 ** 2)
        for anchor in self.route_skeleton:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells(cell, anchor)
            if dist <= min_dist + distance_to_corner_of_cell:
                if dist < min_dist:
                    min_dist = dist
                candidates.add((anchor, dist))

        return {a for a, d in candidates if d <= min_dist + distance_to_corner_of_cell}

    def find_nearest_neighbor_from_candidates(self, point, candidates):
        min_dist = float("inf")
        nearest_anchor = None
        (x, y) = self.calculate_exact_index_for_point(point)
        for candidate in candidates:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells((x,y), candidate)
            if dist < min_dist:
                nearest_anchor = candidate
                min_dist =dist
        return (nearest_anchor, min_dist)

    # Converts cell coordinate to long lat based on initialization_point
    def convert_cell_to_point(self, cell) -> tuple[float, float]:
        offsets = (cell[0] * self.cell_size, cell[1] * self.cell_size)
        
        gps_coordinates = DistanceCalculator.shift_point_with_bearing(self.initialization_point, offsets[0], DistanceCalculator.NORTH)
        gps_coordinates = DistanceCalculator.shift_point_with_bearing(gps_coordinates, offsets[1], DistanceCalculator.EAST)

        return gps_coordinates
