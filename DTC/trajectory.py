from datetime import datetime
from math import floor
from typing import Optional
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator
import config
import json


class Trajectory:
    def __init__(self) -> None:
        self.points = list[Point]()
        self.min_longitude = float('inf')
        self.max_longitude = float('-inf')
        self.min_latitude = float('inf')
        self.max_latitude = float('-inf')
        self.max_timestamp = datetime.min

    def add_point(self,longitude: float, latitude: float, timestamp: datetime = datetime.min, noise: Optional[bool] = False) -> None:
        self.points.append(Point(longitude, latitude, timestamp, noise))

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

        if timestamp is not None:
            self.max_timestamp = max(self.max_timestamp, timestamp)

    def to_dict(self) -> dict:
        return {
            'points': [point.to_dict() for point in self.points if point is not None] if self.points else [],
            'min_longitude': self.min_longitude,
            'max_longitude': self.max_longitude,
            'min_latitude': self.min_latitude,
            'max_latitude': self.max_latitude
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

class TrajectoryPointCloud:
    def __init__(self) -> None:
        self.trajectories = list[Trajectory]()
        self.min_longitude = float('inf')
        self.max_longitude = float('-inf')
        self.min_latitude = float('inf')
        self.max_latitude = float('-inf')
        self.max_timestamp = datetime.min

    def add_trajectory(self, trajectory: Trajectory) -> None:
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
        
        self.max_timestamp = max(self.max_timestamp, trajectory.max_timestamp)

    def get_shifted_min(self) -> tuple[float, float]:
        # Bearing: South (180), West (270)
        shift_distance = config.CELL_SIZE * floor(config.NEIGHBORHOOD_SIZE / 2)

        # Shift min point south and west
        shifted_point = DistanceCalculator.shift_point_with_bearing((self.min_longitude, self.min_latitude), shift_distance, config.WEST)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, shift_distance, config.SOUTH)

        return shifted_point

    def get_shifted_max(self) -> tuple[float, float]:
        # Bearing: North (0), East (90)
        shift_distance = config.CELL_SIZE * floor(config.NEIGHBORHOOD_SIZE / 2)

        # Shift max point north and east
        shifted_point = DistanceCalculator.shift_point_with_bearing((self.max_longitude, self.max_latitude), shift_distance, config.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, shift_distance, config.EAST)

        return shifted_point

    # Bounding rectangle is defined by the tuples (min_lon, min_lat) and (max_lon, max_lat) with some padding added
    def get_bounding_rectangle(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return (self.get_shifted_min(), self.get_shifted_max())

    # Geopy utilizes geodesic distance - shortest distance on the surface of an elipsoid earth model
    def calculate_bounding_rectangle_area(self):
        ((min_long, min_lat),(max_long, max_lat)) = self.get_bounding_rectangle()
        width = DistanceCalculator.get_distance_between_points((min_long, min_lat), (max_long, min_lat))
        height = DistanceCalculator.get_distance_between_points((min_long, min_lat), (min_long, max_lat))

        return (width, height)
