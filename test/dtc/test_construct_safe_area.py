import pytest
from DTC.construct_safe_area import ConstructSafeArea, SafeArea
from DTC.distance_calculator import DistanceCalculator
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
import DTC.json_read_write as json_read_write
from datetime import datetime
from scipy.spatial import KDTree
import config

class TestConstructSafeArea():
    @pytest.fixture
    def two_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0)

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        DistanceCalculator.shift_point_with_bearing(t.points[0], 20, config.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], 20, config.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, config.EAST)
        
        t.add_point(shifted_point[0], shifted_point[1])
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()

        return gs

    def test_create_cover_sets_returns_correctly_with_single_anchor(self, two_point_grid):
        two_point_grid.route_skeleton = {(4, 4)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, True)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((4, 4), (4, 4))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (4, 4))
        
        (p1, d1), (p2, d2) = cs[(4, 4)]
        coordinates_with_dist = {((4, 4), expected_d1), ((8, 8), expected_d2)}

        assert len(cs) == 1
        assert (p1, d1) in coordinates_with_dist
        assert (p2, d2) in coordinates_with_dist

    def test_create_cover_sets_returns_correctly_with_single_anchor_and_no_relaxed_nn(self, two_point_grid):
        two_point_grid.route_skeleton = {(4, 4)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, False)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((4, 4), (4, 4))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (4, 4))
        
        (p1, d1), (p2, d2) = cs[(4, 4)]
        coordinates_with_dist = {((4, 4), expected_d1), ((8, 8), expected_d2)}

        assert len(cs) == 1
        assert (p1, d1) in coordinates_with_dist
        assert (p2, d2) in coordinates_with_dist

    def test_create_cover_sets_returns_correctly_with_two_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(4, 4), (6, 7)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, True)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((4, 4), (4, 4))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (6, 7))
        p1, d1 = list(cs[(4, 4)])[0]
        p2, d2 = list(cs[(6, 7)])[0]

        assert len(cs) == 2
        assert p1 == (4, 4)
        assert d1 == expected_d1

        assert p2 == (8, 8)
        assert d2 == expected_d2


        assert cs[(4, 4)].isdisjoint(cs[(6, 7)])

    def test_create_cover_sets_returns_correctly_with_multiple_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(2, 3), (4, 4), (5, 6), (8, 8)}
        cs = ConstructSafeArea._create_cover_sets(two_point_grid.route_skeleton, two_point_grid.grid, True)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((4, 4), (4, 4))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((8, 8), (8, 8))

        p1, d1 = list(cs[(4, 4)])[0]
        p2, d2 = list(cs[(8, 8)])[0]

        # Length is only gonna be 2 as defaultdict is utilized and (4, 4), (8, 8) does not have any points added
        assert len(cs) == 2
        assert p1 == (4, 4)
        assert d1 == expected_d1

        assert p2 == (8, 8)
        assert d2 == expected_d2
        assert cs[(2, 3)] == set()
        assert cs[(5, 6)] == set()
        assert cs[(4, 4)].isdisjoint(cs[(8, 8)])

    def test_find_candidate_nearest_neighbors_returns_correctly_with_single_anchor(self):
        route_skeleton = {(2, 2)}
        route_skeleton_list = list(route_skeleton)
        route_skeleton_kd_tree = KDTree(route_skeleton_list)

        c1 = (1.5, 1.5)
        c2 = (2.5, 2.5)
        c3 = (3.5, 3.5)

        cnn1 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, c1)
        cnn2 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, c2)
        cnn3 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, c3)

        assert cnn1 == [(2, 2)]
        assert cnn2 == [(2, 2)]
        assert cnn3 == [(2, 2)]

    def test_find_candidate_nearest_neighbors_returns_correctly_with_multiple_anchors(self):
        route_skeleton = {(2, 2), (2.5, 2.5), (3, 3), (4, 4)}
        route_skeleton_list = list(route_skeleton)
        route_skeleton_kd_tree = KDTree(route_skeleton_list)

        c1 = (1.5, 1.5)
        c2 = (2.5, 2.5)
        c3 = (3.5, 3.5)
        
        cnn1 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, c1)
        cnn2 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, c2)
        cnn3 = ConstructSafeArea._find_candidate_nearest_neighbors(route_skeleton_list, route_skeleton_kd_tree, c3)

        assert set(cnn1) == {(2, 2), (2.5, 2.5), (3, 3)}
        assert set(cnn2) == {(2, 2), (2.5, 2.5), (3, 3)}
        assert set(cnn3) == {(2, 2), (2.5, 2.5), (3, 3), (3, 3), (4, 4)}

    def test_creation_from_cover_set_and_from_meta_data_are_equal(self):
        safe_area_file = "test/dtc/resources/safe_area_test.json"
        cover_set = {((1, 1), 1), ((2, 1), 2)}
        anchor = (0, 1)
        decrease_factor = 0
        safe_area_from_cover_set = SafeArea.from_cover_set(cover_set, anchor, decrease_factor, datetime.now().replace(microsecond=0))
        safe_areas_from_cover_set = {anchor: safe_area_from_cover_set}

        json_read_write.write_safe_areas_to_json(safe_area_file, safe_areas_from_cover_set)
        safe_areas_from_json = json_read_write.read_safe_areas_from_json(safe_area_file)

        safe_area_from_json = safe_areas_from_json[anchor]

        assert safe_area_from_cover_set.anchor == safe_area_from_json.anchor
        assert safe_area_from_cover_set.cardinality == safe_area_from_json.cardinality
        assert safe_area_from_cover_set.cardinality_squish == safe_area_from_json.cardinality_squish
        assert safe_area_from_cover_set.confidence == safe_area_from_json.confidence
        assert safe_area_from_cover_set.confidence_change_factor == safe_area_from_json.confidence_change_factor
        assert safe_area_from_cover_set.max_confidence_change == safe_area_from_json.max_confidence_change
        assert safe_area_from_cover_set.decay_factor == safe_area_from_json.decay_factor
        assert safe_area_from_cover_set.timestamp == safe_area_from_json.timestamp
        

