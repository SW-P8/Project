import pytest
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.distance_calculator import DistanceCalculator
from datetime import datetime
from math import floor
from collections import defaultdict
import config

class TestGridsystem():
    @pytest.fixture
    def single_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        return gs

    @pytest.fixture
    def two_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        DistanceCalculator.shift_point_with_bearing(t.points[0], 20, config.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], 20, config.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, config.EAST)
        
        t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        return gs
    
    @pytest.fixture
    def five_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, config.NORTH)
            shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, config.EAST)
        
            t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        return gs

    def test_grid_is_build_correctly(self, two_point_grid):
        assert two_point_grid.grid.keys() == {(4, 4), (8, 8)}

        assert (4, 4) == two_point_grid.grid[(4, 4)][0]

        assert (8, 8) == two_point_grid.grid[(8, 8)][0]

    def test_extract_main_route_returns_correctly_with_single_point(self, single_point_grid):
        single_point_grid.extract_main_route()

        assert single_point_grid.main_route == {(4, 4)}

    def test_extract_main_route_raises_error_correctly(self, single_point_grid):
        with pytest.raises(ValueError) as e:
            single_point_grid.extract_main_route(0.5)
        
        assert str(e.value) == "distance scale must be less than neighborhood size divided by 2"

    def test_extract_main_route_returns_correctly_with_two_points(self, two_point_grid):
        two_point_grid.extract_main_route(0.4)

        assert two_point_grid.main_route == {(4, 4), (8, 8)}

        two_point_grid.main_route = set()
        # Should return an empty set with default d
        two_point_grid.extract_main_route()
        assert two_point_grid.main_route == set()

    def test_extract_main_route_returns_correctly_with_many_points(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        for i in range(1, 11):
            t.add_point(1,0,datetime(2024, 1, 1, 1, 1, i))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], 20, config.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, config.EAST)
        t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 11))

        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()

        # Density center is skewed towards (4, 4) enough that (8, 8) is not included in main route
        assert gs.main_route == {(4, 4)}

    def test_extract_route_skeleton_returns_correctly_with_single_cell(self, single_point_grid):
        single_point_grid.main_route = {(3, 3)}
        single_point_grid.extract_route_skeleton(25, 20, 20)
        assert single_point_grid.route_skeleton == {(3.5, 3.5)}

    def test_extract_route_skeleton_returns_correctly_with_two_cells(self, single_point_grid):
        single_point_grid.main_route = {(3, 3), (12, 3)}
        single_point_grid.grid[(12, 3)].append("some random val")
        single_point_grid.extract_route_skeleton(25, 20, 20)
        assert single_point_grid.route_skeleton == {(8.0, 3.5)}

    def test_extract_route_skeleton_returns_correctly_with_three_cells(self, single_point_grid):
        single_point_grid.main_route = {(3, 3), (28, 3), (33, 3)}
        single_point_grid.grid[(28, 3)].append("some random val")
        single_point_grid.grid[(33, 3)].append(("some random val"))
        single_point_grid.extract_route_skeleton(25, 20, 20)
        assert single_point_grid.route_skeleton == {(16.0, 3.5)}

    def test_construct_safe_areas_returns_correctly_with_two_points_and_single_anchor_and_no_refinement(self, two_point_grid):
        two_point_grid.route_skeleton = {(4, 4)}
        two_point_grid.construct_safe_areas(0)
        
        expected_r = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (4, 4))
        
        assert len(two_point_grid.safe_areas) == 1
        assert two_point_grid.safe_areas[(4, 4)].radius == expected_r

    def test_construct_safe_areas_returns_correctly_with_two_points_and_single_anchor(self, two_point_grid):
        two_point_grid.route_skeleton = {(4, 4)}
        two_point_grid.construct_safe_areas()
        
        expected_r = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (4, 4)) * 0.99

        assert len(two_point_grid.safe_areas) == 1
        assert two_point_grid.safe_areas[(4, 4)].radius == expected_r

    def test_construct_safe_areas_returns_correctly_with_five_points_and_single_anchor(self, five_point_grid):
        five_point_grid.route_skeleton = {(4, 4)}
        five_point_grid.construct_safe_areas()
        
        expected_r = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (4, 4)) * 0.99

        assert len(five_point_grid.safe_areas) == 1
        assert five_point_grid.safe_areas[(4, 4)].radius == expected_r

        # Now expect 2 points to be removed as noise
        five_point_grid.construct_safe_areas(0.4)
        
        p3 = DistanceCalculator.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[2], five_point_grid.initialization_point)
        distance_to_p3 = DistanceCalculator.calculate_euclidian_distance_between_cells(p3, (4, 4)) 

        p4 = DistanceCalculator.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[3], five_point_grid.initialization_point)
        distance_to_p4 = DistanceCalculator.calculate_euclidian_distance_between_cells(p4, (4, 4)) 

        assert len(five_point_grid.safe_areas) == 1
        # As the points are far enough apart, it should result in the 4th point being removed while the 3rd point remains
        # Hence the radius should be smaller than distance to p4 and greater than distance to p3
        assert five_point_grid.safe_areas[(4, 4)].radius < distance_to_p4
        assert five_point_grid.safe_areas[(4, 4)].radius > distance_to_p3
    
    def test_construct_safe_areas_returns_correctly_with_five_points_and_two_anchors(self, five_point_grid):
        # With this split, p1 and p2 belongs to first anchor and p3, p4 and p5 belongs to 2nd anchor
        five_point_grid.route_skeleton = {(3, 3), (8, 8)}
        five_point_grid.construct_safe_areas()
        
        # As mentioned above, the refining radius of safe areas with these splits, will mean that p2 and p3 are removed respectively
        # Thereby yielding radius values just shy of their distance to the anchor points
        p2 = DistanceCalculator.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[1], five_point_grid.initialization_point)
        expected_r1 = DistanceCalculator.calculate_euclidian_distance_between_cells(p2, (3, 3)) * 0.99

        p3 = DistanceCalculator.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[2], five_point_grid.initialization_point)
        expected_r2 = DistanceCalculator.calculate_euclidian_distance_between_cells(p3, (8, 8)) * 0.99

        assert len(five_point_grid.safe_areas) == 2
        assert five_point_grid.safe_areas[(3, 3)].radius == expected_r1
        assert five_point_grid.safe_areas[(8, 8)].radius == expected_r2