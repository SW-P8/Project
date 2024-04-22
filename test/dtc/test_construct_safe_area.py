import pytest
from DTC.construct_safe_area import ConstructSafeArea, SafeArea
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
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, two_point_grid.initialization_point)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (3, 3))
        
        (p1, d1), (p2, d2) = cs[(3, 3)]
        coordinates_with_dist = {(two_point_grid.pc.trajectories[0].points[0].get_coordinates(), expected_d1), (two_point_grid.pc.trajectories[0].points[1].get_coordinates(), expected_d2)}

        assert len(cs) == 1
        assert (p1.get_coordinates(), d1) in coordinates_with_dist
        assert (p2.get_coordinates(), d2) in coordinates_with_dist

    def test_create_cover_sets_returns_correctly_with_two_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3), (5, 6)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, two_point_grid.initialization_point)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (5, 6))
        p1, d1 = list(cs[(3, 3)])[0]
        p2, d2 = list(cs[(5, 6)])[0]

        assert len(cs) == 2
        assert p1.get_coordinates() == two_point_grid.pc.trajectories[0].points[0].get_coordinates()
        assert p1.timestamp == two_point_grid.pc.trajectories[0].points[0].timestamp
        assert d1 == expected_d1

        assert p2.get_coordinates() == two_point_grid.pc.trajectories[0].points[1].get_coordinates()
        assert p2.timestamp == two_point_grid.pc.trajectories[0].points[1].timestamp
        assert d2 == expected_d2


        assert cs[(3, 3)].isdisjoint(cs[(5, 6)])

    def test_create_cover_sets_returns_correctly_with_multiple_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(2, 3), (3, 3), (5, 6), (7, 7)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, two_point_grid.initialization_point)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (7, 7))

        p1, d1 = list(cs[(3, 3)])[0]
        p2, d2 = list(cs[(7, 7)])[0]

        # Length is only gonna be 2 as defaultdict is utilized and (3, 3), (7, 7) does not have any points added
        assert len(cs) == 2
        assert p1.get_coordinates() == two_point_grid.pc.trajectories[0].points[0].get_coordinates()
        assert p1.timestamp == two_point_grid.pc.trajectories[0].points[0].timestamp
        assert d1 == expected_d1

        assert p2.get_coordinates() == two_point_grid.pc.trajectories[0].points[1].get_coordinates()
        assert p2.timestamp == two_point_grid.pc.trajectories[0].points[1].timestamp
        assert d2 == expected_d2
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

class TestSafeArea():
    @pytest.mark.parametrize("normalised_cardinality, expected_result",
        [
            (0.001, -0.053),# test with values for cardinality_offset with cardinality = 100
            (1, 0.019),     # test with values for cardinality_offset with cardinality = 100.000
            (3, 0.400),     # test with values for cardinality_offset with cardinality = 300.000
            (10, 0.899)     # test with values for cardinality_offset with cardinality = 1.000.000
        ]
    )
    def test_sigmoid_as_used_for_cardinality_offset(self, normalised_cardinality, expected_result):
        x_offset = 3
        y_offset = -0.1
        multiplier = 1

        res = SafeArea.sigmoid(normalised_cardinality, x_offset, y_offset, multiplier)

        assert round(res, 3) == expected_result

    # Test for decay with above values x_offset.
    @pytest.mark.parametrize("x_offset, expected_result",
        [
            (-0.053, 0.556),    # test with values for cardinality_offset with cardinality = 100
            (0.019, 0.530),     # test with values for cardinality_offset with cardinality = 100.000
            (0.400, 0.38),      # test with values for cardinality_offset with cardinality = 300.000
            (0.899, 0.149)      # test with values for cardinality_offset with cardinality = 1.000.000
        ]
    )
    def test_sigmoid_as_used_for_decay_with_delta_0_05(self, x_offset, expected_result):
        delta_decay = (1 / 60 * 60 * 24) * 0.05
        y_offset = -0.5
        multiplier = 2

        res = SafeArea.sigmoid(delta_decay, x_offset, y_offset, multiplier)

        assert round(res, 3) == expected_result

