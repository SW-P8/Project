import pytest
import trajectory
from datetime import datetime

class TestTrajectoryPointCloud():
    def test_adding_trajectory_updates_min_max(self):
        pc = trajectory.TrajectoryPointCloud()

        # min,max should be set to infity or negative infinity when trajectory point cloud is empty
        assert len(pc.trajectories) == 0
        assert pc.max_longitude == float("-inf")
        assert pc.min_longitude == float("inf")
        assert pc.max_latitude == float("-inf")
        assert pc.min_latitude == float("inf")

        t = trajectory.Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t)

        # adding any single point trajectory to an empty trajectory point cloud should result in that trajectory's being both min and max
        assert len(pc.trajectories) == 1
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

    def test_max_longitude_updates_correctly(self):
        pc = trajectory.TrajectoryPointCloud()
        t1 = trajectory.Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a greather longitude should only update max_longitude
        t2 = trajectory.Trajectory()
        t2.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 2
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

        # adding a longitude within the bounds of min and max should not change anything
        t3 = trajectory.Trajectory()
        t3.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 2
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

    def test_min_longitude_updates_correctly(self):
        pc = trajectory.TrajectoryPointCloud()
        t1 = trajectory.Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a lesser longitude should only update min_longitude
        t2 = trajectory.Trajectory()
        t2.add_point(0,0,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 0
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

        # adding a longitude within the bounds of min and max should not change anything
        t3 = trajectory.Trajectory()
        t3.add_point(0.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 0
        assert pc.max_latitude == 0
        assert pc.min_latitude == 0

    def test_max_latitude_updates_correctly(self):
        pc = trajectory.TrajectoryPointCloud()
        t1 = trajectory.Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a larger latitude should only update max_latitude
        t2 = trajectory.Trajectory()
        t2.add_point(1,1,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 1
        assert pc.min_latitude == 0

        # adding a latitude within the bounds of min and max should not change anything
        t3 = trajectory.Trajectory()
        t3.add_point(1,0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 1
        assert pc.min_latitude == 0

    def test_min_latitude_updates_correctly(self):
        pc = trajectory.TrajectoryPointCloud()
        t1 = trajectory.Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        pc.add_trajectory(t1)

        # adding a lesser latitude should only update min_latitude
        t2 = trajectory.Trajectory()
        t2.add_point(1,-1,datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t2)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == -1

        # adding a latitude within the bounds of min and max should not change anything
        t3 = trajectory.Trajectory()
        t3.add_point(1,-0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)
        assert pc.max_longitude == 1
        assert pc.min_longitude == 1
        assert pc.max_latitude == 0
        assert pc.min_latitude == -1

    def test_bounding_rectangle_is_correct(self):
        pc = trajectory.TrajectoryPointCloud()

        # trajectory providing max_longitude (2)
        t1 = trajectory.Trajectory()
        t1.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t1.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        t1.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t1)

        # trajectory providing min_longitude (0)
        t2 = trajectory.Trajectory()
        t2.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t2.add_point(0,0,datetime(2024, 1, 1, 1, 1, 2))
        t2.add_point(0.5,0,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t2)

        # trajectory providing max_latitude (1)
        t3 = trajectory.Trajectory()
        t3.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t3.add_point(1,1,datetime(2024, 1, 1, 1, 1, 2))
        t3.add_point(1,0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t3)

        # trajectory providing min_latitude (-1)
        t4 = trajectory.Trajectory()
        t4.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        t4.add_point(1,-1,datetime(2024, 1, 1, 1, 1, 2))
        t4.add_point(1,-0.5,datetime(2024, 1, 1, 1, 1, 3))
        pc.add_trajectory(t4)

        assert pc.get_bounding_rectangle() == ((0,-1), (2,1))


