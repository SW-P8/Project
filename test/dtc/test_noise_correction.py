import pytest
from DTC import trajectory, gridsystem, noise_correction
from datetime import datetime
from geopy import distance
import copy
from DTC.utils.constants import NORTH, EAST

class TestGridsystem():    
    @pytest.fixture
    def five_point_grid(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,1,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = distance.distance(meters=i * 5).destination((t.points[0].latitude, t.points[0].longitude), NORTH)
            shifted_point = distance.distance(meters=i * 5).destination((shifted_point), EAST)
        
            t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc) 
        gs.create_grid_system()
        return gs
        
    def test_calculate_average_point(self):
        p1 = trajectory.Point(2, 2)
        p2 = trajectory.Point(20, -80)
        p3 = trajectory.Point(6, 6)
        
        expected_avg = trajectory.Point(4, 4)

        noise_correction.NoiseCorrection.calculate_average_point(p2, p1, p3)

        assert expected_avg.latitude == p2.latitude
        assert expected_avg.longitude == p2.longitude
   
    # Given that point[1] is shifted 5 meters it should be at anchor (5,5)
    def test_correct_noisy_point_should_not_change(self, five_point_grid):
        nc = noise_correction.NoiseCorrection(five_point_grid)
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7.5,7.5), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        nc.correct_noisy_point(nc.gridsystem.pc.trajectories[0], 1)
        
        expected_point = nc.gridsystem.convert_cell_to_point((5,5))

        assert nc.gridsystem.pc.trajectories[0].points[1].longitude == expected_point.longitude
        assert nc.gridsystem.pc.trajectories[0].points[1].latitude == expected_point.latitude

    def test_correct_noisy_point_should_change_anchor_with_timestamp(self, five_point_grid):
        nc = noise_correction.NoiseCorrection(five_point_grid)
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        # Changing point to make it an outlier.
        shifted_point = distance.distance(meters=200).destination((nc.gridsystem.pc.trajectories[0].points[3].latitude, nc.gridsystem.pc.trajectories[0].points[3].longitude), NORTH)
        shifted_point = distance.distance(meters=200).destination((shifted_point), EAST)

        nc.gridsystem.pc.trajectories[0].points[3].longitude = shifted_point[1]
        nc.gridsystem.pc.trajectories[0].points[3].latitude = shifted_point[0]

        nc.correct_noisy_point(nc.gridsystem.pc.trajectories[0], 3)
        
        expected_point = nc.gridsystem.convert_cell_to_point((7,7), nc.gridsystem.pc.trajectories[0].points[3].timestamp)

        assert nc.gridsystem.pc.trajectories[0].points[3].longitude == expected_point.longitude
        assert nc.gridsystem.pc.trajectories[0].points[3].latitude == expected_point.latitude
        assert nc.gridsystem.pc.trajectories[0].points[3].timestamp == expected_point.timestamp

    def test_correct_noisy_point_with_timestamp_none(self, five_point_grid):
        nc = noise_correction.NoiseCorrection(five_point_grid)
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        nc.gridsystem.pc.trajectories[0].points[3].timestamp = None

        nc.correct_noisy_point(nc.gridsystem.pc.trajectories[0], 3)

        assert nc.gridsystem.pc.trajectories[0].points[3].timestamp == None

    # test should not correct any points
    def test_noise_detection_no_noise(self, five_point_grid):
        nc = noise_correction.NoiseCorrection(five_point_grid)

        expected_trajectory = nc.gridsystem.pc.trajectories[0]
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        nc.noise_detection(nc.gridsystem.pc.trajectories[0])

        assert nc.gridsystem.pc.trajectories[0] == expected_trajectory

    def test_noise_detection_correct_noisy_point(self, five_point_grid):
        nc = noise_correction.NoiseCorrection(five_point_grid)
    
        trajectory_before_correction = copy.deepcopy(nc.gridsystem.pc.trajectories[0])

        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        # Changing point to make it an outlier.
        shifted_point = distance.distance(meters=200).destination((nc.gridsystem.pc.trajectories[0].points[3].latitude, nc.gridsystem.pc.trajectories[0].points[3].longitude), NORTH)
        shifted_point = distance.distance(meters=200).destination((shifted_point), EAST)

        nc.gridsystem.pc.trajectories[0].points[3].longitude = shifted_point[1]
        nc.gridsystem.pc.trajectories[0].points[3].latitude = shifted_point[0]

        
        nc.noise_detection(nc.gridsystem.pc.trajectories[0])
        
        expected_corrected_point = nc.gridsystem.convert_cell_to_point((7,7))

        assert nc.gridsystem.pc.trajectories[0] != trajectory_before_correction 
        assert nc.gridsystem.pc.trajectories[0].points[3].longitude == expected_corrected_point.longitude
        assert nc.gridsystem.pc.trajectories[0].points[3].latitude == expected_corrected_point.latitude

