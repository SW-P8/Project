from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator
from DTC.construct_safe_area import ConstructSafeArea
from DTC.construct_main_route import ConstructMainRoute
from DTC.route_skeleton import RouteSkeleton
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
    
    def extract_route_skeleton(self, smooth_radius: int = 25, filtering_list_radius: int = 20, distance_interval: int = 20):
        self.route_skeleton = RouteSkeleton.extract_route_skeleton(self.main_route, smooth_radius, filtering_list_radius, distance_interval)

    def construct_safe_areas(self, decrease_factor: float = 0.01):
        self.safe_areas = ConstructSafeArea.construct_safe_areas(self.route_skeleton, self.grid, self.populated_cells, decrease_factor, self.initialization_point, self.cell_size)

