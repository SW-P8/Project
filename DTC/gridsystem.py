from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator
# from DTC.safe_area import SafeArea
from DTC.construct_safe_area import ConstructSafeArea
from DTC.construct_main_route import ConstructMainRoute
from math import floor, sqrt
from operator import itemgetter
from datetime import datetime
from typing import Optional

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
        # self.safe_areas = dict()
        self.safe_areas = dict()

    def create_grid_system(self):
        # Fill grid with points
        for trajectory in self.pc.trajectories:
            for point in trajectory.points:
                (x,y) = DistanceCalculator.calculate_exact_index_for_point(point, self.initialization_point, self.cell_size)
                floored_index = (floor(x), floor(y))
                if floored_index not in self.populated_cells:
                    self.populated_cells.add(floored_index)
                    self.grid[floored_index] = list()
                self.grid[floored_index].append(point)
    
    def extract_main_route(self, distance_scale: float = 0.2):
        self.main_route = ConstructMainRoute.extract_main_route(self.populated_cells, self.neighborhood_size, self.grid, distance_scale)
    
    def calculate_density_center(self, index):
        return ConstructMainRoute.calculate_density_center(index, self.neighborhood_size, self.populated_cells, self.grid)
    
    def extract_route_skeleton(self, smooth_radius: int = 25, filtering_list_radius: int = 20, distance_interval: int = 20):
        smr = self.smooth_main_route(smooth_radius)
        cmr = self.filter_outliers_in_main_route(smr, filtering_list_radius)
        self.route_skeleton = self.sample_main_route(cmr, distance_interval)
        
    def smooth_main_route(self, radius: int = 25) -> set:
        smr = set()
        for (x1, y1) in self.main_route:
            ns = {(x2, y2) for (x2, y2) in self.main_route if DistanceCalculator.calculate_euclidian_distance_between_cells((x1 + 0.5, y1 + 0.5), (x2 + 0.5, y2 + 0.5)) <= radius}
            x_sum = sum(x for x, _ in ns) + len(ns) * 0.5
            y_sum = sum(y for _, y in ns) + len(ns) * 0.5

            if x_sum != 0:
                x_sum /= len(ns)

            if y_sum != 0:
                y_sum /= len(ns)
            smr.add((x_sum, y_sum))
        return smr
    
    def filter_outliers_in_main_route(self, smr: set, radius_prime: int = 20):
        cmr = set()
        for (x1, y1) in smr:
            targets = {(x2, y2) for (x2, y2) in smr if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= radius_prime}
            if len(targets) >= 0.01 * len(smr):
                cmr.add((x1, y1))
        return cmr
    
    def sample_main_route(self, cmr: set, distance_interval: int = 20):
        rs = set()
        for c1 in cmr:
            targets = {c2 for c2 in cmr if DistanceCalculator.calculate_euclidian_distance_between_cells(c1, c2) <= distance_interval}
            # targets should be greater than 1 to take self into account
            if len(targets) > 1:
                rs.add(c1)
        return rs

    def construct_safe_areas(self, decrease_factor: float = 0.01):
        self.safe_areas = ConstructSafeArea.construct_safe_areas(self.route_skeleton, self.grid, self.populated_cells, decrease_factor, self.initialization_point, self.cell_size)

