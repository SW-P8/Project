import pytest
import trajectory
from datetime import datetime

class TestTrajectory():
    def test_adding_point_updates_min_max(self):
        t = trajectory.Trajectory()

        # min,max should be set to infity or negative infinity when trajectory is empty
        assert len(t.points) == 0
        assert t.max_longitude == float("-inf")
        assert t.min_longitude == float("inf")
        assert t.max_latitude == float("-inf")
        assert t.min_latitude == float("inf")

        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # adding any point to an empty trajectory should result in that point being both min and max
        assert len(t.points) == 1
        assert t.max_longitude == 1
        assert t.min_longitude == 1
        assert t.max_latitude == 0
        assert t.min_latitude == 0

    def test_max_longitude_updates_correctly(self):
        t = trajectory.Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # adding a greather longitude should only update max_longitude
        t.add_point(2,0,datetime(2024, 1, 1, 1, 1, 2))
        assert t.max_longitude == 2
        assert t.min_longitude == 1
        assert t.max_latitude == 0
        assert t.min_latitude == 0

        # adding a longitude within the bounds of min and max should not change anything
        t.add_point(1.5,0,datetime(2024, 1, 1, 1, 1, 3))
        assert t.max_longitude == 2
        assert t.min_longitude == 1
        assert t.max_latitude == 0
        assert t.min_latitude == 0

    def test_min_longitude_updates_correctly(self):
        t = trajectory.Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # adding a lesser longitude should only update min_longitude
        t.add_point(0,0,datetime(2024, 1, 1, 1, 1, 2))
        assert t.max_longitude == 1
        assert t.min_longitude == 0
        assert t.max_latitude == 0
        assert t.min_latitude == 0

        # adding a longitude within the bounds of min and max should not change anything
        t.add_point(0.5,0,datetime(2024, 1, 1, 1, 1, 3))
        assert t.max_longitude == 1
        assert t.min_longitude == 0
        assert t.max_latitude == 0
        assert t.min_latitude == 0

    def test_max_latitude_updates_correctly(self):
        t = trajectory.Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # adding a larger latitude should only update max_latitude
        t.add_point(1,1,datetime(2024, 1, 1, 1, 1, 2))
        assert t.max_longitude == 1
        assert t.min_longitude == 1
        assert t.max_latitude == 1
        assert t.min_latitude == 0

        # adding a latitude within the bounds of min and max should not change anything
        t.add_point(1,0.5,datetime(2024, 1, 1, 1, 1, 3))
        assert t.max_longitude == 1
        assert t.min_longitude == 1
        assert t.max_latitude == 1
        assert t.min_latitude == 0

    def test_min_latitude_updates_correctly(self):
        t = trajectory.Trajectory()
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # adding a lesser latitude should only update min_latitude
        t.add_point(1,-1,datetime(2024, 1, 1, 1, 1, 2))
        assert t.max_longitude == 1
        assert t.min_longitude == 1
        assert t.max_latitude == 0
        assert t.min_latitude == -1

        # adding a latitude within the bounds of min and max should not change anything
        t.add_point(1,-0.5,datetime(2024, 1, 1, 1, 1, 3))
        assert t.max_longitude == 1
        assert t.min_longitude == 1
        assert t.max_latitude == 0
        assert t.min_latitude == -1

