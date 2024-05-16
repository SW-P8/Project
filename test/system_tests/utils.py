import math
class SquareCircleBuilder:
    EARTH_RADIUS = 6378137 
    LAT_CENTER = 4.5        
    LON_CENTER = 172.5      
    DISTANCE_BETWEEN_CENTERS = 150  

    def meters_to_degrees_lat(meters):
        return meters / 111320

    def meters_to_degrees_lon(meters, latitude):
        return meters / (111320 * math.cos(math.radians(latitude)))

    def build_circle(self):
        circle_center_lat = self.LAT_CENTER - self.meters_to_degrees_lat(50)
        circle_center_lon = self.LON_CENTER
        square_center_lat = self.LAT_CENTER + self.meters_to_degrees_lat(self.DISTANCE_BETWEEN_CENTERS)
        square_center_lon = self.LON_CENTER 
   
        half_side = 50 
        square_vertices = [
            (square_center_lat + self.meters_to_degrees_lat(half_side), square_center_lon + self.meters_to_degrees_lon(half_side, square_center_lat)),
            (square_center_lat + self.meters_to_degrees_lat(half_side), square_center_lon - self.meters_to_degrees_lon(half_side, square_center_lat)),
            (square_center_lat - self.meters_to_degrees_lat(half_side), square_center_lon - self.meters_to_degrees_lon(half_side, square_center_lat)),
            (square_center_lat - self.meters_to_degrees_lat(half_side), square_center_lon + self.meters_to_degrees_lon(half_side, square_center_lat))
        ]

        circle_radius = 50 
        num_circle_points = 100 
        circle_points = [
            (
                circle_center_lat + self.meters_to_degrees_lat(circle_radius * math.sin(2 * math.pi * i / num_circle_points)),
                circle_center_lon + self.meters_to_degrees_lon(circle_radius * math.cos(2 * math.pi * i / num_circle_points), circle_center_lat)
            )
            for i in range(num_circle_points)
        ]




