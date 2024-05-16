import pytest
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.noise_correction import NoiseCorrection
from DTC.distance_calculator import DistanceCalculator
import copy

class TestNoiseCorrection():    
    @pytest.fixture
    def five_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,1)

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, DistanceCalculator.NORTH)
            shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, DistanceCalculator.EAST)
        
            t.add_point(shifted_point[0], shifted_point[1])
        pc.add_trajectory(t)
        gs = GridSystem(pc) 
        gs.create_grid_system()
        return gs
   
    # Given that point[1] is shifted 5 meters it should be at anchor (5,5)
    def test_correct_noisy_point_should_not_change(self, five_point_grid):
        
        five_point_grid.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7.5,7.5), (10,10)}
        five_point_grid.construct_safe_areas(0)

        nc = NoiseCorrection(five_point_grid.safe_areas, five_point_grid.initialization_point)
        nc.correct_noisy_point(five_point_grid.pc.trajectories[0], 1)
        
        expected_point = DistanceCalculator.convert_cell_to_point(five_point_grid.initialization_point, (5,5))

        assert five_point_grid.pc.trajectories[0].points[1].longitude == expected_point[0]
        assert five_point_grid.pc.trajectories[0].points[1].latitude == expected_point[1]

    def test_correct_noisy_point_should_change_anchor_with_timestamp(self, five_point_grid):
        
        five_point_grid.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        five_point_grid.construct_safe_areas(0)
        nc = NoiseCorrection(five_point_grid.safe_areas, five_point_grid.initialization_point)
        original_timestamp = five_point_grid.pc.trajectories[0].points[3].timestamp

        # Changing point to make it an outlier.
        shifted_point = DistanceCalculator.shift_point_with_bearing(five_point_grid.pc.trajectories[0].points[0], 200, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 200, DistanceCalculator.EAST)

        five_point_grid.pc.trajectories[0].points[3].longitude = shifted_point[0]
        five_point_grid.pc.trajectories[0].points[3].latitude = shifted_point[1]

        nc.correct_noisy_point(five_point_grid.pc.trajectories[0], 4)
        
        expected_point = DistanceCalculator.convert_cell_to_point(five_point_grid.initialization_point, (7,7))

        assert five_point_grid.pc.trajectories[0].points[3].longitude == expected_point[0]
        assert five_point_grid.pc.trajectories[0].points[3].latitude == expected_point[1]
        assert five_point_grid.pc.trajectories[0].points[3].timestamp == original_timestamp

    def test_correct_noisy_point_with_timestamp_none(self, five_point_grid):
        
        five_point_grid.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        five_point_grid.construct_safe_areas(0)

        five_point_grid.pc.trajectories[0].points[3].timestamp = None

        # Changing point to make it an outlier.
        shifted_point = DistanceCalculator.shift_point_with_bearing(
            five_point_grid.pc.trajectories[0].points[0], 200, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(
            shifted_point, 200, DistanceCalculator.EAST)

        five_point_grid.pc.trajectories[0].points[3].longitude = shifted_point[0]
        five_point_grid.pc.trajectories[0].points[3].latitude = shifted_point[1]

        nc = NoiseCorrection(five_point_grid.safe_areas, five_point_grid.initialization_point)
        nc.correct_noisy_point(five_point_grid.pc.trajectories[0], 4)

        expected_point = DistanceCalculator.convert_cell_to_point(
            five_point_grid.initialization_point, (7, 7))

        assert five_point_grid.pc.trajectories[0].points[3].timestamp == None
        assert five_point_grid.pc.trajectories[0].points[3].longitude == expected_point[0]
        assert five_point_grid.pc.trajectories[0].points[3].latitude == expected_point[1]

    # Test should not correct any points
    def test_noise_detection_no_noise(self, five_point_grid):

        expected_trajectory = five_point_grid.pc.trajectories[0]
        
        five_point_grid.route_skeleton = {(0,0), (2.5,2.5), (5,5), (7,7), (10,10)}
        five_point_grid.construct_safe_areas(0)
        
        nc = NoiseCorrection(five_point_grid.safe_areas, five_point_grid.initialization_point)
        nc.noise_detection(five_point_grid.pc.trajectories[0])

        assert five_point_grid.pc.trajectories[0] == expected_trajectory

    def test_noise_detection_correct_noisy_point(self, five_point_grid):

        trajectory_before_correction = copy.deepcopy(five_point_grid.pc.trajectories[0])
        five_point_grid.route_skeleton = {(0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            if safe_area.radius == 0:
                safe_area.radius = 0.01  # As confidence update is a part of nosie detection, a safe area cannot have 0 as its radius.

        nc = NoiseCorrection(five_point_grid.safe_areas, five_point_grid.initialization_point)
        # Changing point to make it an outlier.
        shifted_point = DistanceCalculator.shift_point_with_bearing(five_point_grid.pc.trajectories[0].points[0], 200, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 200, DistanceCalculator.EAST)

        five_point_grid.pc.trajectories[0].points[3].longitude = shifted_point[0]
        five_point_grid.pc.trajectories[0].points[3].latitude = shifted_point[1]

        nc.noise_detection(five_point_grid.pc.trajectories[0])

        expected_corrected_point = DistanceCalculator.convert_cell_to_point(five_point_grid.initialization_point, (7, 7.5))

        assert five_point_grid.pc.trajectories[0] != trajectory_before_correction 
        assert five_point_grid.pc.trajectories[0].points[3].longitude == expected_corrected_point[0]
        assert five_point_grid.pc.trajectories[0].points[3].latitude == expected_corrected_point[1]

    def test_check_list_front_when_bad_trajectory_should_remove(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            if safe_area.radius == 0:
                # As confidence update is a part of nosie detection, a safe area cannot have 0 as its radius.
                safe_area.radius = 0.01

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for i in range(10):
            trajectory.add_point(10*i, 10*i, noise=True)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points)

        # Assert
        assert 0 == len(trajectory.points)
        assert 10 == len(cleaned_points)

    def test_check_list_front_when_five_bad_points_should_remove_half(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            safe_area.radius = 10

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for i in range(5):
            trajectory.add_point(10*i, 10*i, noise=True)
        for i in range(5):
            trajectory.add_point(1.0001348, 1.0001582, noise=True)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points)

        # Assert
        assert 5 == len(trajectory.points)
        assert 5 == len(cleaned_points)

    def test_list_check_front_if_no_noise_dont_remove_any(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            safe_area.radius = 10

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for i in range(10):
            trajectory.add_point(1.0001348, 1.0001582, False)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points)

        # Assert
        assert 10 == len(trajectory.points)
        assert 0 == len(cleaned_points)

    def test_check_list_back_when_bad_trajectory_should_remove(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            if safe_area.radius == 0:
                # As confidence update is a part of nosie detection, a safe area cannot have 0 as its radius.
                safe_area.radius = 0.01

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for i in range(10):
            trajectory.add_point(10*i, 10*i, noise=True)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points, True)

        # Assert
        assert 0 == len(trajectory.points)
        assert 10 == len(cleaned_points)

    def test_check_list_back_when_five_bad_points_should_remove_half(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            safe_area.radius = 10

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for i in range(5):
            trajectory.add_point(1.0001348, 1.0001582, noise=True)
        for i in range(5):
            trajectory.add_point(10*i, 10*i, noise=True)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points, True)

        # Assert
        assert 5 == len(trajectory.points)
        assert 5 == len(cleaned_points)

    def test_list_check_back_if_no_noise_dont_remove_any(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            safe_area.radius = 10

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for i in range(10):
            trajectory.add_point(1.0001348, 1.0001582, False)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points, True)

        # Assert
        assert 10 == len(trajectory.points)
        assert 0 == len(cleaned_points)

    def test_check_noise_front_back_no_noise(self, five_point_grid):
        # Arrange
        five_point_grid.route_skeleton = {
            (0, 0), (3.5, 3.5), (5, 5), (7, 7.5), (10, 10)}
        five_point_grid.construct_safe_areas(0)
        for safe_area in five_point_grid.safe_areas.values():
            safe_area.radius = 10

        nc = NoiseCorrection(five_point_grid.safe_areas,
                             five_point_grid.initialization_point)
        cleaned_points = list()
        trajectory = Trajectory()
        for _ in range(4):
            trajectory.add_point(1.0001348, 1.0001582, False)
        for _ in range(2):
            trajectory.add_point(10, 10, True)
        for _ in range(4):
            trajectory.add_point(1.0001348, 1.0001582, False)

        # Act
        nc._check_list_trajectory(trajectory, cleaned_points, True)

        # Assert
        assert 10 == len(trajectory.points)
        assert 0 == len(cleaned_points)
