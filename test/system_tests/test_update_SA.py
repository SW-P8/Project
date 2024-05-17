import datetime
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.construct_safe_area import Point
from DTC.noise_correction import NoiseCorrection 
import copy
import matplotlib.pyplot as plt
import math
class SquareCircleBuilder:
    EARTH_RADIUS = 6378137 
    LAT_CENTER = 4.5        
    LON_CENTER = 172.5      
    DISTANCE_BETWEEN_CENTERS = 15000  
    NUM_POINTS = 10000

    def meters_to_degrees_lat(self, meters):
        return meters / 111320

    def meters_to_degrees_lon(self, meters, latitude):
        return meters / (111320 * math.cos(math.radians(latitude)))

    def build_circle_square(self):
        circle_center_lat = self.LAT_CENTER - self.meters_to_degrees_lat(50)
        circle_center_lon = self.LON_CENTER
        square_center_lat = self.LAT_CENTER + self.meters_to_degrees_lat(self.DISTANCE_BETWEEN_CENTERS)
        square_center_lon = self.LON_CENTER 
   
        half_side = 5000  # Half the side length in meters
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
            square_points.append((lon, lat))

        circle_radius = 5000 
        num_circle_points = self.NUM_POINTS 
        circle_points = [
            (
                circle_center_lon + self.meters_to_degrees_lat(circle_radius * math.sin(2 * math.pi * i / num_circle_points)),
                circle_center_lat + self.meters_to_degrees_lon(circle_radius * math.cos(2 * math.pi * i / num_circle_points), circle_center_lat)
            )
            for i in range(num_circle_points)
        ]
        return (square_points, circle_points)









class TestIterativeCorrection():    
    #@pytest.fixture
    def fifty_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()

        # Add initial point
        
        points = self.points_to_lat_lon(1000, False)
        t.add_point(points[0][0], points[0][1])
        for point in points:
            t.add_point(point[0], point[1], datetime.datetime.now())

        pc.add_trajectory(t)
        gs = GridSystem(pc) 
        gs.create_grid_system()
        gs.extract_main_route()
        gs.extract_route_skeleton()
        gs.construct_safe_areas()
        return gs
    
    def my_plot(self,figname, coordinates):
        lons, lats = zip(*coordinates)
        
        plt.figure(figsize=(10, 10))
        plt.scatter(lons, lats, c='blue', marker='o')
        plt.axis('scaled')
        plt.title('Safe Area Coordinates')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)
        
        plt.savefig(f'{figname}.png')


    def points_to_lat_lon(self, number_of_points, lat_change):
        import math

        lat = 4.5 
        distance_m = 10  
        earth_radius = 6378137  

        def meters_to_degrees_longitude(meters, latitude):
            return meters / (111320 * math.cos(math.radians(latitude)))

        delta_lon = meters_to_degrees_longitude(distance_m, lat)

        start_lon = 172.5  # Starting longitude
        if not lat_change:
            lon_lat_coordinates = [(start_lon + i * delta_lon, lat) for i in range(number_of_points)]
        else:
            lon_lat_coordinates = [(start_lon + number_of_points/2 * delta_lon, lat + i * delta_lon) for i in range(number_of_points)]
        return lon_lat_coordinates



    def run_test(self):
        gs = self.fifty_point_grid()
        points = self.points_to_lat_lon(500, False)
        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        t = Trajectory()
        for point in points:
            point_ = Point(point[0], point[1], datetime.datetime.now())
            t.add_point(point_.longitude, point_.latitude, point_.timestamp)
        noise_corrector.noise_detection(t)

        a =  copy.copy(gs.safe_areas)

        points_y_shift = self.points_to_lat_lon(500, True)
        self.my_plot("shifted_points", points_y_shift)
        self.my_plot("non_shifted_points", points)

        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        t = Trajectory()
        for point in points_y_shift:
            point_ = Point(point[0], point[1], (datetime.datetime.now() + datetime.timedelta(days=10)))
            t.add_point(point_.longitude, point_.latitude, point_.timestamp)

        print(noise_corrector.noise_detection(t))


        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        noise_corrector.noise_detection(t)
        coordinates = list(a.keys())
        self.my_plot("safe_area_plot", coordinates)
        coordinates = list(gs.safe_areas.keys())
        self.my_plot("safe_area_plot_shifted", coordinates)
        
    def run_test_2(self):
        sbuild = SquareCircleBuilder()
        points_square, points_circle = sbuild.build_circle_square()
        points = []
        t = Trajectory()
        pc = TrajectoryPointCloud()
        squares = copy.copy(points_square)
        circles = copy.copy(points_circle)
        points.extend(squares)
        points.extend(circles)
        for point in points:
            t.add_point(point[0], point[1], datetime.datetime.now())
            #t.add_point(point_)
        pc.add_trajectory(t)
        gs = GridSystem(pc=pc)
        gs.create_grid_system()
        gs.extract_main_route()
        gs.extract_route_skeleton()
        gs.construct_safe_areas()
        coordinates = list(gs.safe_areas.keys())
        self.my_plot("safe_areas_circle_square", coordinates)
        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        for point in circles:
            point_ = Point(point[0], point[1], (datetime.datetime.now() + datetime.timedelta(days=10)))
            t.add_point(point_.longitude, point_.latitude + sbuild.meters_to_degrees_lat(15000), point_.timestamp)
        for point in squares:
            point_ = Point(point[0], point[1], (datetime.datetime.now() + datetime.timedelta(days=10)))
            t.add_point(point_.longitude, point_.latitude - sbuild.meters_to_degrees_lat(15000), point_.timestamp)
        print(noise_corrector.noise_detection(t))


        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        noise_corrector.noise_detection(t)
        coordinates = list(gs.safe_areas.keys())
        self.my_plot("safe_area_plot_shifted", coordinates)
            
             
        
#e = TestIterativeCorrection()
#e.run_test()


e = SquareCircleBuilder()
a, e = e.build_circle_square()
k = TestIterativeCorrection()
k.my_plot("square", a)
k.my_plot("circle", e)
a.extend(e)
k.my_plot("circle_square", a)
k.run_test_2()