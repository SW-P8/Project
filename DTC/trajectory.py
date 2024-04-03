from datetime import datetime
from math import floor
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator

class Trajectory:
    def __init__(self) -> None:
        self.points = list[Point]()
        self.min_longitude = float('inf')
        self.max_longitude = float('-inf')
        self.min_latitude = float('inf')
        self.max_latitude = float('-inf')

    def add_point(self,longitude: float, latitude: float, timestamp: datetime) -> None:
        self.points.append(Point(longitude, latitude, timestamp))

        # Check if added longitude is new max
        if longitude > self.max_longitude:
            self.max_longitude = longitude
        
        # Check if added longitude is new min
        if longitude < self.min_longitude:
            self.min_longitude = longitude

        # Check if added latitude is ither new max
        if latitude > self.max_latitude:
            self.max_latitude = latitude

        # Check if added latitude is ither new max
        if latitude < self.min_latitude:
            self.min_latitude = latitude

class TrajectoryPointCloud:
    def __init__(self, cell_size = 5, neighborhood_size = 9) -> None:
        self.trajectories = list[Trajectory]()
        self.min_longitude = float('inf')
        self.max_longitude = float('-inf')
        self.min_latitude = float('inf')
        self.max_latitude = float('-inf')
        self.cell_size = cell_size        #Based on observation in DTC paper that minimal width of a road is 5m
        self.neighborhood_size = neighborhood_size #To be determined but DTC uses 9

    def add_trajectory(self,trajectory: Trajectory) -> None:
        self.trajectories.append(trajectory)

        # Check if added trajectory contains new max longitude
        if trajectory.max_longitude > self.max_longitude:
            self.max_longitude = trajectory.max_longitude

        # Check if added trajectory contains new min longitude
        if trajectory.min_longitude < self.min_longitude:
            self.min_longitude = trajectory.min_longitude

        # Check if added trajectory contains new max latitude
        if trajectory.max_latitude > self.max_latitude:
            self.max_latitude = trajectory.max_latitude

        # Check if added trajectory contains new min latitude
        if trajectory.min_latitude < self.min_latitude:
            self.min_latitude = trajectory.min_latitude

    def get_shifted_min(self) -> tuple[float, float]:
        #Bearing: South (180), West (270)
        shift_distance = self.cell_size * floor(self.neighborhood_size / 2)

        # Shift min point south and west
        shifted_point = DistanceCalculator.shift_point_with_bearing((self.min_longitude, self.min_latitude), shift_distance, DistanceCalculator.WEST)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, shift_distance, DistanceCalculator.SOUTH)

        return shifted_point
    
    def get_shifted_max(self) -> tuple[float, float]:
        #Bearing: North (0), East (90)
        shift_distance = self.cell_size * floor(self.neighborhood_size / 2)

        # Shift max point north and east
        shifted_point = DistanceCalculator.shift_point_with_bearing((self.max_longitude, self.max_latitude), shift_distance, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, shift_distance, DistanceCalculator.EAST)

        return shifted_point

    # Bounding rectangle is defined by the tuples (min_lon, min_lat) and (max_lon, max_lat) with some padding added
    def get_bounding_rectangle(self) -> tuple[tuple[float, float], tuple[float,float]]:
        return (self.get_shifted_min(), self.get_shifted_max())
    
    # Geopy utilizes geodesic distance - shortest distance on the surface of an elipsoid earth model
    def calculate_bounding_rectangle_area(self):
        ((min_long, min_lat),(max_long, max_lat)) = self.get_bounding_rectangle()
        width = DistanceCalculator.get_distance_between_points((min_long, min_lat), (max_long, min_lat))
        height = DistanceCalculator.get_distance_between_points((min_long, min_lat), (min_long, max_lat))

        return (width, height)
