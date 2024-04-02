from math import sqrt
from DTC.trajectory import Point
from geopy import distance
from enum import Enum

class DistanceCalculator(Enum):
    NORTH = 0
    East = 90
    SOUTH = 180
    WEST = 270
    
    @staticmethod
    def shift_point_with_bearing(point, bearing):
        if type(point) == Point:
            (longitude, latitude) = point.get_coordinates()
        else:
            (longitude, latitude) = point

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
    def calculate_euclidian_distance_between_cells(cell1, cell2):
        (x_1, y_1) = cell1
        (x_2, y_2) = cell2
        return sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)