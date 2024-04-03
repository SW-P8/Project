from math import sqrt
from DTC.point import Point
from geopy import distance

class DistanceCalculator():
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270
    
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