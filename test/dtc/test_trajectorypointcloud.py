from DTC.trajectory import Trajectory, TrajectoryPointCloud
from datetime import datetime
from DTC.distance_calculator import DistanceCalculator
import pytest

class TestTrajectoryPointCloud():
    def test_adding_trajectory_updates_min_max(self):
        pc = TrajectoryPointCloud()

        # min,max should be set to infity or negative infinity when trajectory point cloud is empty
        assert len(pc.trajectories) == 0
        assert pc.max_longitude == float("-inf")
        assert pc.min_longitude == float("inf")
        assert pc.max_latitude == float("-inf")
        assert pc.min_latitude == float("inf")

        t = Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t)

        # adding any single point trajectory to an empty trajectory point cloud should result in that trajectory's being both min and max
        assert len(pc.trajectories) == 1
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

    def test_max_longitude_updates_correctly(self):
        pc = TrajectoryPointCloud()
        t1 = Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a greather longitude should only update max_longitude
        t2 = Trajectory()
        t2.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 2
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

        # adding a longitude within the bounds of min and max should not change anything
        t3 = Trajectory()
        t3.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 2
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

    def test_min_longitude_updates_correctly(self):
        pc = TrajectoryPointCloud()
        t1 = Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a lesser longitude should only update min_longitude
        t2 = Trajectory()
        t2.add_point(0,0,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 0
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

        # adding a longitude within the bounds of min and max should not change anything
        t3 = Trajectory()
        t3.add_point(0.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 0
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

    def test_max_latitude_updates_correctly(self):
        pc = TrajectoryPointCloud()
        t1 = Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a larger latitude should only update max_latitude
        t2 = Trajectory()
        t2.add_point(1,1,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 1
        assert pc.min_latitude == 0

        # adding a latitude within the bounds of min and max should not change anything
        t3 = Trajectory()
        t3.add_point(1,0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 1
        assert pc.min_latitude == 0

    def test_min_latitude_updates_correctly(self):
        pc = TrajectoryPointCloud()
        t1 = Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a lesser latitude should only update min_latitude
        t2 = Trajectory()
        t2.add_point(1,-1,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == -1

        # adding a latitude within the bounds of min and max should not change anything
        t3 = Trajectory()
        t3.add_point(1,-0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == -1

    def test_min_point_shifted_correctly(self):
        pc = TrajectoryPointCloud()
        # By default shifting by 4 cells of size 5 meters
        expected_shift_distance = 20

        # trajectories provide min point (1,0)
        t = Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        t.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t)

        (shifted_min_long, shifted_min_lat) = pc.get_shifted_min()

        # distance shifted south
        shifted_south_distance = DistanceCalculator.get_distance_between_points((shifted_min_long, pc.min_latitude), (shifted_min_long, shifted_min_lat))

        # distance shifted west
        shifted_west_distance = DistanceCalculator.get_distance_between_points((pc.min_longitude, shifted_min_lat), (shifted_min_long, shifted_min_lat))

        # Shifting points south and west should yield lesser long and lat
        assert shifted_min_long < pc.min_longitude
        assert shifted_min_lat < pc.min_latitude
        assert shifted_south_distance == expected_shift_distance
        assert shifted_west_distance == expected_shift_distance

    def test_max_point_shifted_correctly(self):
        pc = TrajectoryPointCloud()
        # By default shifting by 4 cells of size 5 meters
        expected_shift_distance = 20

        # trajectories provide min point (1,0)
        t = Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        t.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t)

        (shifted_max_long, shifted_max_lat) = pc.get_shifted_max()

        # distance shifted north
        shifted_north_distance = DistanceCalculator.get_distance_between_points((shifted_max_long, pc.max_latitude), (shifted_max_long, shifted_max_lat))

        # distance shifted east
        shifted_east_distance = DistanceCalculator.get_distance_between_points((pc.max_longitude, shifted_max_lat), (shifted_max_long, shifted_max_lat))

        # Shifting north and east should yield greater long and lat
        assert shifted_max_long > pc.max_longitude
        assert shifted_max_lat > pc.max_latitude
        assert shifted_north_distance == expected_shift_distance
        assert shifted_east_distance == expected_shift_distance
        

    def test_bounding_rectangle_is_correct(self):
        pc = TrajectoryPointCloud()

        # trajectory providing max_longitude (2)
        t1 = Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t1.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        t1.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t1)

        # trajectory providing min_longitude (0)
        t2 = Trajectory()
        t2.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t2.add_point(0,0,datetime(2024, 1, 1, 1, 1, 2))
        t2.add_point(0.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t2)

        # trajectory providing max_latitude (1)
        t3 = Trajectory()
        t3.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t3.add_point(1,1,datetime(2024, 1, 1, 1, 1, 2))
        t3.add_point(1,0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)

        # trajectory providing min_latitude (-1)
        t4 = Trajectory()
        t4.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t4.add_point(1,-1,datetime(2024, 1, 1, 1, 1, 2))
        t4.add_point(1,-0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t4)

        (shifted_width, shifted_height) = pc.calculate_bounding_rectangle_area()
        # non_shifted_br  ((0,-1), (2,1))
        expected_width = 222645.28
        expected_height = 221188.78

        assert expected_width == pytest.approx(shifted_width)
        assert expected_height == pytest.approx(shifted_height)

