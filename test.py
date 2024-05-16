import pytest
import datetime
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.point import Point
from DTC.noise_correction import NoiseCorrection 
import copy
import matplotlib.pyplot as plt



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
        plt.figure(figsize=(10, 6))
        plt.scatter(lons, lats, c='blue', marker='o')
        plt.title('Safe Area Coordinates')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
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
        #gs.construct_safe_areas()
        #gs.construct_safe_areas()
        print("first_point_set")
        points = self.points_to_lat_lon(500, False)
        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        t = Trajectory()
        for point in points:
            point_ = Point(point[0], point[1], datetime.datetime.now())
            t.add_point(point_.longitude, point_.latitude, point_.timestamp)
        noise_corrector.noise_detection(t)

        a =  copy.copy(gs.safe_areas)

        print("second_point_set")
        points_y_shift = self.points_to_lat_lon(500, True)
        self.my_plot("shifted_points", points_y_shift)
        self.my_plot("non_shifted_points", points)


        for k, v in gs.safe_areas.items():
            v.radius = 5
        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        t = Trajectory()
        for point in points_y_shift:
            point_ = Point(point[0], point[1], (datetime.datetime.now() + datetime.timedelta(days=10)))
            t.add_point(point_.longitude, point_.latitude, point_.timestamp)

        print(noise_corrector.noise_detection(t))


        noise_corrector = NoiseCorrection(gs.safe_areas, gs.initialization_point, gs.main_route)
        noise_corrector.noise_detection(t)
        for v1  in gs.safe_areas.values():
            print(v1.anchor)

        print("\n\n\n")
        for v1  in a.values():
            print(v1.anchor)
        print(len(gs.safe_areas), len(a))
        coordinates = list(a.keys())
        self.my_plot("safe_area_plot", coordinates)
        coordinates = list(gs.safe_areas.keys())
        self.my_plot("safe_area_plot_shifted", coordinates)
        
e = TestIterativeCorrection()
e.run_test()