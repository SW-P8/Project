from math import sqrt
from DTC.point import Point
from geopy import distance
from typing import Optional

class DistanceCalculator():
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

    @staticmethod
    def calculate_exact_index_for_point(point: Point, initialization_point: tuple[float, float], cell_size: float):
        # Calculate x index
        x_offset = DistanceCalculator.get_distance_between_points(initialization_point, (point.longitude, initialization_point[1]))
        x_coordinate = (x_offset / cell_size) - 1

        # Calculate y index
        y_offset = DistanceCalculator.get_distance_between_points(initialization_point, (initialization_point[0], point.latitude))
        y_coordinate = (y_offset / cell_size) - 1

        return (x_coordinate, y_coordinate)
   
    @staticmethod
    def shift_point_with_bearing(point, shift_dist: float, bearing: float):
        if type(point) == Point:
            (longitude, latitude) = point.get_coordinates()
        else:
            (longitude, latitude) = point

        shifted_point = distance.distance(meters=shift_dist).destination((latitude, longitude), bearing)
        return (shifted_point.longitude, shifted_point.latitude)

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
    def find_nearest_neighbor_from_candidates(point, candidates, initialization_point: tuple[float, float], cell_size: float) -> tuple[tuple[float, float], float]:
        min_dist = float("inf")
        nearest_anchor: Optional[tuple[float, float]] = None
        (x, y) = DistanceCalculator.calculate_exact_index_for_point(point, initialization_point, cell_size)
        for candidate in candidates:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells((x,y), candidate)
            if dist < min_dist:
                nearest_anchor = candidate
                min_dist = dist

        return (nearest_anchor, min_dist)
 
    # Converts cell coordinate to long lat based on initialization_point
    @staticmethod
    def convert_cell_to_point(initialization_point: tuple[float, float], cell: tuple[float, float], cell_size: float) -> tuple[float, float]:
        offsets = (cell[0] * cell_size, cell[1] * cell_size)
        
        gps_coordinates = DistanceCalculator.shift_point_with_bearing(initialization_point, offsets[0], DistanceCalculator.NORTH)
        gps_coordinates = DistanceCalculator.shift_point_with_bearing(gps_coordinates, offsets[1], DistanceCalculator.EAST)

        return gps_coordinates
    
    @staticmethod 
    def calculate_euclidian_distance_between_cells(cell1, cell2):
        (x_1, y_1) = cell1
        (x_2, y_2) = cell2
        return sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)
    
    @staticmethod
    def calculate_average_position(p1: Point, p2: Point):
        (x1, y1) = p1.get_coordinates()
        (x2, y2) = p2.get_coordinates()

        x_avg = (x1 + x2) / 2
        y_avg = (y1 + y2) / 2
        return Point(x_avg, y_avg)
