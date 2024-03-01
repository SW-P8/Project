from datetime import datetime
from geopy import distance
from typing import Any

class Point:
    def __init__(self, longitude: float, latitude: float, timestamp: datetime) -> None:
        self.longitude = longitude
        self.latitude = latitude
        self.timestamp = timestamp

    def get_coordinates(self) -> tuple[float, float]:
        return (self.longitude, self.latitude)

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
    def __init__(self) -> None:
        self.trajectories = list[Trajectory]()
        self.min_longitude = float('inf')
        self.max_longitude = float('-inf')
        self.min_latitude = float('inf')
        self.max_latitude = float('-inf')
        self.cell_size = 5         #Based on observation in DTC paper that minimal width of a road is 5m
        self.neighborhood_size = 9 #To be determined but DTC uses 9

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

    # Bouding rectangle is defined by the tuples (min_lon, min_lat) and (max_lon, max_lat) with some padding added
    def get_bounding_rectangle(self) -> tuple[tuple[float, float], tuple[float,float]]:

        #TODO: add padding to bounding rectangle
        return ((self.min_longitude, self.min_latitude), (self.max_longitude, self.max_latitude))
    
    # Geopy utilizes geodesic distance - shortest distance on the surface of an elipsoid earth model
    def calculate_bouding_rectangle_area(self):
        ((min_long, min_lat),(max_long, max_lat)) = self.get_bounding_rectangle()
        width = distance.distance((min_long, min_lat), (max_long, min_lat)).meters
        height = distance.distance((min_long, min_lat), (min_long, max_lat)).meters
