import pytest
from DTC.construct_safe_area import ConstructSafeArea
from DTC.distance_calculator import DistanceCalculator
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem

class TestConstructSafeArea():
    @pytest.fixture
    def two_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0)

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        DistanceCalculator.shift_point_with_bearing(t.points[0], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, DistanceCalculator.EAST)
        
        t.add_point(shifted_point[0], shifted_point[1])
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()

        return gs

    def test_create_cover_sets_returns_correctly_with_single_anchor(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, two_point_grid.populated_cells, two_point_grid.initialization_point)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (3, 3))

        assert len(cs) == 1
        assert cs[(3, 3)] == {(two_point_grid.pc.trajectories[0].points[0], expected_d1), (two_point_grid.pc.trajectories[0].points[1], expected_d2)}

    def test_create_cover_sets_returns_correctly_with_two_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3), (5, 6)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, two_point_grid.populated_cells, two_point_grid.initialization_point)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (5, 6))

        assert len(cs) == 2
        assert cs[(3, 3)] == {(two_point_grid.pc.trajectories[0].points[0], expected_d1)}
        assert cs[(5, 6)] == {(two_point_grid.pc.trajectories[0].points[1], expected_d2)}
        assert cs[(3, 3)].isdisjoint(cs[(5, 6)])

    def test_create_cover_sets_returns_correctly_with_multiple_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(2, 3), (3, 3), (5, 6), (7, 7)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, two_point_grid.populated_cells, two_point_grid.initialization_point)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (7, 7))

        assert len(cs) == 4
        assert cs[(3, 3)] == {(two_point_grid.pc.trajectories[0].points[0], expected_d1)}
        assert cs[(7, 7)] == {(two_point_grid.pc.trajectories[0].points[1], expected_d2)}
        assert cs[(2, 3)] == set()
        assert cs[(5, 6)] == set()
        assert cs[(3, 3)].isdisjoint(cs[(7, 7)])

    def test_find_candidate_nearest_neighbors_returns_correctly_with_single_anchor(self):
        route_skeleton = {(2, 2)}

        c1 = (1.5, 1.5)
        c2 = (2.5, 2.5)
        c3 = (3.5, 3.5)

        cnn1 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton, c1)
        cnn2 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton, c2)
        cnn3 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton, c3)

        assert cnn1 == {(2, 2)}
        assert cnn2 == {(2, 2)}
        assert cnn3 == {(2, 2)}

    def test_find_candidate_nearest_neighbors_returns_correctly_with_multiple_anchors(self):
        route_skeleton = {(2, 2), (2.5, 2.5), (3, 3), (4, 4)}

        c1 = (1.5, 1.5)
        c2 = (2.5, 2.5)
        c3 = (3.5, 3.5)
        
        cnn1 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton, c1)
        cnn2 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton, c2)
        cnn3 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton, c3)

        assert cnn1 == {(2, 2), (2.5, 2.5)}
        assert cnn2 == {(2, 2), (2.5, 2.5), (3, 3)}
        assert cnn3 == {(2.5, 2.5), (3, 3), (4, 4)}

