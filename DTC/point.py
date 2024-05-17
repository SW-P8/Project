from typing import Optional
from datetime import datetime


class Point:
    def __init__(self, longitude: float, latitude: float, timestamp: Optional[datetime] = None, noise: Optional[bool] = False) -> None:
        self.longitude = longitude
        self.latitude = latitude
        self.timestamp = timestamp
        self.noise = noise

    def get_coordinates(self) -> tuple[float, float]:
        return (self.longitude, self.latitude)

    def set_coordinates(self, new_coordinates):
        self.longitude = new_coordinates[0]
        self.latitude = new_coordinates[1]

    def to_dict(self) -> dict:
        return {
            'longitude': self.longitude,
            'latitude': self.latitude,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'noise': self.noise
        }
