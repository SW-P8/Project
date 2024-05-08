import pytest
from datetime import datetime
import random
import copy
from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.distance_calculator import DistanceCalculator
from DTC.clean_trajectory import CleanTrajectory
from DTC.construct_safe_area import Point


# Fixtures for GridSystem and Point objects
# Tests for the CleanTraj class
class TestCleanTrajectory:

    @pytest.fixture
    def grid_system(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, DistanceCalculator.NORTH)
            shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, DistanceCalculator.EAST)
        
            t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()
        gs.extract_route_skeleton()
        gs.construct_safe_areas()
        for _,safe_area in gs.safe_areas.items():
            safe_area.radius = 5
            safe_area.timestamp = datetime.now()
            safe_area.cardinality = random.randint(1, 12)
        return gs

    @pytest.fixture
    def trajectory(self):
        trajectory = Trajectory()
        trajectory.add_point(116.37677, 39.88791, datetime.now())
        trajectory.add_point(116.38033, 39.88795, datetime.now())
        trajectory.add_point(116.39392, 39.89014, datetime.now())
        return trajectory

    def test_init(self, grid_system: GridSystem):
        clean_traj = CleanTrajectory(grid_system.safe_areas, grid_system.route_skeleton, grid_system.initialization_point)
        assert clean_traj.initialization_point == grid_system.initialization_point
        assert clean_traj.route_skeleton == grid_system.route_skeleton
        assert isinstance(clean_traj.safe_areas, dict)

    def test_clean(self, grid_system, trajectory):
        # Arrange
        clean_trajectory = CleanTrajectory(grid_system.safe_areas, grid_system.route_skeleton, grid_system.initialization_point)
        old_trajectory = copy.deepcopy(trajectory)
        safe_area_anchor = [anchor for anchor in grid_system.safe_areas][0]
        old_safe_area = copy.deepcopy(grid_system.safe_areas[safe_area_anchor])

        # Act
        clean_trajectory.clean(trajectory)

        # Assert
        assert 3 == len(trajectory.points)
        # This cehck how many points are different. One point from the old trajectory does not go into the safe-area, so there should be one point of difference.
        assert 1 == len(
            set((point.longitude, point.latitude) for point in old_trajectory.points) - set((point.longitude, point.latitude) for point in trajectory.points))
        # We want to check if the point clouds of the safe areas are filled when a trajectory is cleaned.
        assert 0 == len(old_safe_area.points_in_safe_area.points)
        assert 0 != len(grid_system.safe_areas[safe_area_anchor].points_in_safe_area.points) 


tester = TestCleanTrajectory()


class test_methods:
    def grid_system(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, DistanceCalculator.NORTH)
            shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, DistanceCalculator.EAST)
        
            t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()
        gs.extract_route_skeleton()
        gs.construct_safe_areas()
        for _,safe_area in gs.safe_areas.items():
            safe_area.radius = 5
            safe_area.timestamp = datetime.now()
            safe_area.cardinality = random.randint(1, 12)
        return gs

    def trajectory(self):
        trajectory = Trajectory()
        trajectory.add_point(116.37677, 39.88791, datetime.now())
        trajectory.add_point(116.38033, 39.88795, datetime.now())
        trajectory.add_point(116.39392, 39.89014, datetime.now())
        return trajectory


fixtures = test_methods()


tester.test_clean(fixtures.grid_system(), fixtures.trajectory())