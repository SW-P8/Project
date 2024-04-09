from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator
# from DTC.safe_area import SafeArea
from DTC.construct_safe_area import ConstructSafeArea
from math import floor, sqrt
from operator import itemgetter
from datetime import datetime
from typing import Optional
from DTC.route_skeleton import RouteSkeletonWrapper

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
        for trajectory in self.pc.trajectories:
            for point in trajectory.points:
                (x,y) = DistanceCalculator.calculate_exact_index_for_point(point, self.initialization_point, self.cell_size)
                floored_index = (floor(x), floor(y))
                if floored_index not in self.populated_cells:
                    self.populated_cells.add(floored_index)
                    self.grid[floored_index] = list()
                self.grid[floored_index].append(point)
    
    def extract_main_route(self, distance_scale: float = 0.2):
        if distance_scale >= 0.5:
            raise ValueError("distance scale must be less than neighborhood size divided by 2")
        distance_threshold = distance_scale * self.neighborhood_size

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
        self.route_skeleton = rsw.route_skeleton.route_skeleton

    def construct_safe_areas(self, decrease_factor: float = 0.01):
        self.safe_areas = ConstructSafeArea.construct_safe_areas(self.route_skeleton, self.grid, self.populated_cells, decrease_factor, self.initialization_point, self.cell_size)

