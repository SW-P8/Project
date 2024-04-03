import pytest
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.noise_correction import NoiseCorrection
from DTC.distance_calculator import DistanceCalculator
from datetime import datetime
import copy

class TestGridsystem():    
    @pytest.fixture
    def five_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,1,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, DistanceCalculator.NORTH)
            shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, DistanceCalculator.EAST)
        
            t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = GridSystem(pc) 
        gs.create_grid_system()
        return gs
   
    # Given that point[1] is shifted 5 meters it should be at anchor (5,5)
    def test_correct_noisy_point_should_not_change(self, five_point_grid):
        nc = NoiseCorrection(five_point_grid)
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7.5,7.5), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        nc.correct_noisy_point(nc.gridsystem.pc.trajectories[0], 1)
        
        expected_point = nc.gridsystem.convert_cell_to_point((5,5))

        assert nc.gridsystem.pc.trajectories[0].points[1].longitude == expected_point.longitude
        assert nc.gridsystem.pc.trajectories[0].points[1].latitude == expected_point.latitude

    def test_correct_noisy_point_should_change_anchor_with_timestamp(self, five_point_grid):
        nc = NoiseCorrection(five_point_grid)
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        # Changing point to make it an outlier.
        shifted_point = DistanceCalculator.shift_point_with_bearing(nc.gridsystem.pc.trajectories[0].points[0], 200, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 200, DistanceCalculator.EAST)

        nc.gridsystem.pc.trajectories[0].points[3].longitude = shifted_point[0]
        nc.gridsystem.pc.trajectories[0].points[3].latitude = shifted_point[1]

        nc.correct_noisy_point(nc.gridsystem.pc.trajectories[0], 3)
        
        expected_point = nc.gridsystem.convert_cell_to_point((5,5), nc.gridsystem.pc.trajectories[0].points[3].timestamp)

        assert nc.gridsystem.pc.trajectories[0].points[3].longitude == expected_point.longitude
        assert nc.gridsystem.pc.trajectories[0].points[3].latitude == expected_point.latitude
        assert nc.gridsystem.pc.trajectories[0].points[3].timestamp == expected_point.timestamp

    def test_correct_noisy_point_with_timestamp_none(self, five_point_grid):
        nc = NoiseCorrection(five_point_grid)
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        nc.gridsystem.pc.trajectories[0].points[3].timestamp = None

        nc.correct_noisy_point(nc.gridsystem.pc.trajectories[0], 3)

        assert nc.gridsystem.pc.trajectories[0].points[3].timestamp == None

    # test should not correct any points
    def test_noise_detection_no_noise(self, five_point_grid):
        nc = NoiseCorrection(five_point_grid)

        expected_trajectory = nc.gridsystem.pc.trajectories[0]
        
        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        nc.noise_detection(nc.gridsystem.pc.trajectories[0])

        assert nc.gridsystem.pc.trajectories[0] == expected_trajectory

    def test_noise_detection_correct_noisy_point(self, five_point_grid):
        nc = NoiseCorrection(five_point_grid)
    
        trajectory_before_correction = copy.deepcopy(nc.gridsystem.pc.trajectories[0])

        nc.gridsystem.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        nc.gridsystem.construct_safe_areas(0)

        # Changing point to make it an outlier.
        shifted_point = DistanceCalculator.shift_point_with_bearing(nc.gridsystem.pc.trajectories[0].points[0], 200, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 200, DistanceCalculator.EAST)

        nc.gridsystem.pc.trajectories[0].points[3].longitude = shifted_point[0]
        nc.gridsystem.pc.trajectories[0].points[3].latitude = shifted_point[1]

        
        nc.noise_detection(nc.gridsystem.pc.trajectories[0])
        
        expected_corrected_point = nc.gridsystem.convert_cell_to_point((5,5))

        assert nc.gridsystem.pc.trajectories[0] != trajectory_before_correction 
        assert nc.gridsystem.pc.trajectories[0].points[3].longitude == expected_corrected_point.longitude
        assert nc.gridsystem.pc.trajectories[0].points[3].latitude == expected_corrected_point.latitude

