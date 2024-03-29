import pytest
from DTC import trajectory, gridsystem, noise_correction
from datetime import datetime
from geopy import distance

class TestGridsystem():    
    @pytest.fixture
    def five_point_grid(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = distance.distance(meters=i * 5).destination((t.points[0].latitude, t.points[0].longitude), 0)
            shifted_point = distance.distance(meters=i * 5).destination((shifted_point), 90)
        
            t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        return gs

    # def test_calculate_average_point(self):
    #     pc = trajectory.TrajectoryPointCloud()
    #     t = trajectory.Trajectory()

    #     # Add point to use initialization point
    #     t.add_point(2, 2, datetime(2024, 1, 1, 1, 1, 1))
    #     # t.add_point(80, -80, datetime(2024, 1, 1, 1, 1, 2))
    #     t.add_point(3, 3, datetime(2024, 1, 1, 1, 1, 3))

    #     pc.add_trajectory(t)
    #     gs = gridsystem.GridSystem(pc)
    #     gs.create_grid_system()

    #     # nc = noise_correction.NoiseCorrection(gs)
    #     
    #     # noise_correction.NoiseCorrection.calculate_average_point(t.points[1], t.points[0], t.points[2])
    #     
    #     assert t.points[0].longitude == 2
        
    def test_calculate_average_point(self):
        p1 = trajectory.Point(2, 2)
        p2 = trajectory.Point(20, -80)
        p3 = trajectory.Point(6, 6)
        
        expected_avg = trajectory.Point(4, 4)

        p2 = noise_correction.NoiseCorrection.calculate_average_point(p1, p3)

        assert expected_avg.latitude == p2.latitude
        assert expected_avg.longitude == p2.longitude
