from math import sqrt
from DTC.point import Point
from geopy import distance
from typing import Optional
from scipy.spatial import KDTree
import config

class DistanceCalculator():

    @staticmethod
    def calculate_exact_index_for_point(point: Point, initialization_point: tuple) -> tuple:
        # Calculate x index
        x_offset = DistanceCalculator.get_distance_between_points(initialization_point, (point.longitude, initialization_point[1]))
        if point.longitude < initialization_point[0]:
            x_offset = -x_offset
        x_coordinate = (x_offset / config.CELL_SIZE)

        # Calculate y index
        y_offset = DistanceCalculator.get_distance_between_points(initialization_point, (initialization_point[0], point.latitude))
        if point.latitude < initialization_point[1]:
            y_offset = -y_offset
        y_coordinate = (y_offset / config.CELL_SIZE)

        return (round(x_coordinate, 2), round(y_coordinate, 2))
   
    @staticmethod
    def shift_point_with_bearing(point, shift_dist: float, bearing: float) -> tuple:
        if type(point) == Point:
            (longitude, latitude) = point.get_coordinates()
        else:
            (longitude, latitude) = point

        shifted_point = distance.distance(meters=shift_dist).destination((latitude, longitude), bearing)
        return (round(shifted_point.longitude, 7), round(shifted_point.latitude, 7))

    @staticmethod
    def get_distance_between_points(source, target):
        if type(source) == Point:
            (longitude1, latitude1) = source.get_coordinates()
        else:
            (longitude1, latitude1) = source
        
        if type(target) == Point:
            (longitude2, latitude2) = target.get_coordinates()
        else:
            (longitude2, latitude2) = target

        # Round distance to cm precision
        return round(distance.distance((latitude1, longitude1), (latitude2, longitude2)).meters, 2)
    
    @staticmethod
    def find_nearest_neighbor_from_candidates(point, candidates: set, initialization_point: tuple) -> tuple[tuple[float, float], float]:
        """
    Find the nearest neighbor of a given point from a set of candidate points.

    Parameters:
        point (Union[Point, Tuple[float, float]]): The point for which to find the nearest neighbor. 
                                                     This can be either a Point object or a tuple of floats representing coordinates in the grid system.
        candidates (Set[Tuple[float, float]]): A set of candidate points from which to search for the nearest neighbor.
        initialization_point (Tuple[float, float]): A tuple representing the initialization point used for calculations.

    Returns:
        Tuple[Tuple[float, float], float]: A tuple containing the nearest neighbor point and the distance to it.

    Note:
        The type of point can be either a Point object or a tuple of floats representing coordinates.
    """
        min_dist = float("inf")
        nearest_anchor: Optional[tuple[float, float]] = None
        if type(point) == Point:
            (x, y) = DistanceCalculator.calculate_exact_index_for_point(point, initialization_point)
        else:
            (x, y) = point

        for candidate in candidates:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells((x,y), candidate)
            if dist < min_dist:
                nearest_anchor = candidate
                min_dist = dist

        return (nearest_anchor, min_dist)
    
    @staticmethod
    def find_nearest_neighbour_from_candidates_with_kd_tree(point, candidates: list, candidates_kd_tree: KDTree, initialization_point: tuple = None) -> tuple[tuple[float, float], float]:
        if type(point) == Point:
            (x, y) = DistanceCalculator.calculate_exact_index_for_point(point, initialization_point)
        else:
            (x, y) = point
        min_dist, nn_index = candidates_kd_tree.query((x, y))
        return (candidates[nn_index], min_dist)

    # Converts cell coordinate to long lat based on initialization_point
    @staticmethod
    def convert_cell_to_point(initialization_point: tuple, cell: tuple) -> tuple:
        offsets = (cell[0] * config.CELL_SIZE, cell[1] * config.CELL_SIZE)
        
        gps_coordinates = DistanceCalculator.shift_point_with_bearing(initialization_point, offsets[0], config.EAST)
        gps_coordinates = DistanceCalculator.shift_point_with_bearing(gps_coordinates, offsets[1], config.NORTH)

        return gps_coordinates
    
    @staticmethod 
    def calculate_euclidian_distance_between_cells(cell1: tuple, cell2: tuple) -> float:
        (x_1, y_1) = cell1
        (x_2, y_2) = cell2
        return sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)
    
    @staticmethod
    def calculate_average_position(p1: Point, p2: Point) -> Point:
        (x1, y1) = p1.get_coordinates()
        (x2, y2) = p2.get_coordinates()

        x_avg = (x1 + x2) / 2
        y_avg = (y1 + y2) / 2

        return Point(x_avg, y_avg)

