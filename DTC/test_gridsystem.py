import pytest
import trajectory, gridsystem
from geopy import distance
from datetime import datetime
from math import sqrt

class TestGridsystem():
    def test_calculate_index_for_point_is_correct(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)

        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        
        (x1, y1) = gs.calculate_index_for_point(t.points[0])
        assert (2, 3) == (x1, y1)

        (x2, y2) = gs.calculate_index_for_point(t.points[1])
        assert (6, 6) == (x2, y2)

    def test_grid_is_build_correctly(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)

        gs.create_grid_system()
        actual_x_size = len(gs.grid)
        assert actual_x_size == 13

        actual_y_size = len(gs.grid[0])
        assert actual_y_size == 12

        assert gs.populated_cells == {(2, 3), (6, 6)}

        assert gs.pc.trajectories[0].points[0] == gs.grid[2][3][0]
        assert gs.pc.trajectories[0].points[1] == gs.grid[6][6][0]

    def test_calculate_euclidian_distance_returns_correctly(self):
        c1 = (0, 0)
        c2 = (1, 0)
        c3 = (0, 1)
        c4 = (1, 1)

        d_c1_c1 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c1)
        d_c1_c2 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c2)
        d_c1_c3 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c3)
        d_c1_c4 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c4)


        assert d_c1_c1 == 0
        assert d_c1_c2 == 1
        assert d_c1_c3 == 1
        assert d_c1_c4 == sqrt(2)

    def test_calculate_density_center_returns_correctly_with_single_point(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()

        density_center = gs.calculate_density_center((2, 3))

        assert density_center == (2, 3)

    def test_calculate_density_center_returns_correctly_with_two_points(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 2))


        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()

        density_center1 = gs.calculate_density_center((2, 3))
        density_center2 = gs.calculate_density_center((6, 6))

        # Density center should be the same as their neighborhoods intersect and they are the only points
        assert density_center1 == (4, 4.5)
        assert density_center2 == (4, 4.5)

    def test_calculate_density_center_returns_correctly_with_many_points(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        for i in range(1, 11):
            t.add_point(1,0,datetime(2024, 1, 1, 1, 1, i))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 11))


        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()

        density_center1 = gs.calculate_density_center((2, 3))
        density_center2 = gs.calculate_density_center((6, 6))

        # Density center should be skewed towards (2,3) as the quantity of points in this cell is higher
        assert density_center1 == (26 / 11, 36 / 11)
        assert density_center2 == (26 / 11, 36 / 11)

    def test_extract_main_route_returns_correctly_with_single_point(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()

        assert gs.main_route == {(2, 3)}

    def test_extract_main_route_returns_correctly_with_two_points(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 2))


        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()

        assert gs.main_route == {(2, 3), (6, 6)}

    def test_extract_main_route_returns_correctly_with_many_points(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        for i in range(1, 11):
            t.add_point(1,0,datetime(2024, 1, 1, 1, 1, i))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 11))


        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()

        # Density center is skewed towards (2, 3) enough that (6, 6) is not included in main route
        assert gs.main_route == {(2, 3)}