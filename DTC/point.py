from typing import Optional
from datetime import datetime

class Point:
    def __init__(self, longitude: float, latitude: float, timestamp: Optional[datetime] = None) -> None:
        self.longitude = longitude
        self.latitude = latitude
        self.timestamp = timestamp
    
    noise_flag = False

    def get_coordinates(self) -> tuple[float, float]:
        return (self.longitude, self.latitude)

    def set_coordinates(self, new_coordinates):
        self.longitude = new_coordinates[0]
        self.latitude = new_coordinates[1]