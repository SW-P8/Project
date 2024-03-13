import pytest
import trajectory, gridsystem
from geopy import distance
from datetime import datetime

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
