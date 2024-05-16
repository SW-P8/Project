import math
import matplotlib.pyplot as plt
class SquareCircleBuilder:
    EARTH_RADIUS = 6378137 
    LAT_CENTER = 4.5        
    LON_CENTER = 172.5      
    DISTANCE_BETWEEN_CENTERS = 150  
    NUM_POINTS = 100

    def meters_to_degrees_lat(self, meters):
        return meters / 111320

    def meters_to_degrees_lon(self, meters, latitude):
        return meters / (111320 * math.cos(math.radians(latitude)))

    def build_circle_square(self):
        circle_center_lat = self.LAT_CENTER - self.meters_to_degrees_lat(50)
        circle_center_lon = self.LON_CENTER
        square_center_lat = self.LAT_CENTER + self.meters_to_degrees_lat(self.DISTANCE_BETWEEN_CENTERS)
        square_center_lon = self.LON_CENTER 
   
        half_side = 50  # Half the side length in meters
        square_points = []
        for i in range(self.NUM_POINTS):
            if i < self.NUM_POINTS / 4:
                # Top edge
                lat = square_center_lat + self.meters_to_degrees_lat(half_side)
                lon = square_center_lon + self.meters_to_degrees_lon(half_side - (i / (self.NUM_POINTS / 4) * 2 * half_side), square_center_lat)
            elif i < self.NUM_POINTS / 2:
                # Right edge
                lat = square_center_lat + self.meters_to_degrees_lat(half_side - ((i - self.NUM_POINTS / 4) / (self.NUM_POINTS / 4) * 2 * half_side))
                lon = square_center_lon - self.meters_to_degrees_lon(half_side, square_center_lat)
            elif i < 3 * self.NUM_POINTS / 4:
                # Bottom edge
                lat = square_center_lat - self.meters_to_degrees_lat(half_side)
                lon = square_center_lon - self.meters_to_degrees_lon(half_side - ((i - self.NUM_POINTS / 2) / (self.NUM_POINTS / 4) * 2 * half_side), square_center_lat)
            else:
                # Left edge
                lat = square_center_lat - self.meters_to_degrees_lat(half_side - ((i - 3 * self.NUM_POINTS / 4) / (self.NUM_POINTS / 4) * 2 * half_side))
                lon = square_center_lon + self.meters_to_degrees_lon(half_side, square_center_lat)
            square_points.append((lat, lon))

        circle_radius = 50 
        num_circle_points = self.NUM_POINTS 
        circle_points = [
            (
                circle_center_lat + self.meters_to_degrees_lat(circle_radius * math.sin(2 * math.pi * i / num_circle_points)),
                circle_center_lon + self.meters_to_degrees_lon(circle_radius * math.cos(2 * math.pi * i / num_circle_points), circle_center_lat)
            )
            for i in range(num_circle_points)
        ]
        return (square_points, circle_points)





