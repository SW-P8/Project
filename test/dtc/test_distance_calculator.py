import pytest
from DTC.distance_calculator import DistanceCalculator
from DTC.point import Point
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from math import sqrt

class TestDistanceCalculator:
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

    def test_convert_cell_to_point(self):
        cell = (10,10)
        cell_size = 5
        initialization_point = (1, 1)

        new_point = DistanceCalculator.convert_cell_to_point(initialization_point, cell, cell_size)
        shift_distance = cell_size * 10

        expected_point = DistanceCalculator.shift_point_with_bearing(initialization_point, shift_distance, DistanceCalculator.NORTH)
        expected_point = DistanceCalculator.shift_point_with_bearing(expected_point, shift_distance, DistanceCalculator.EAST)

        assert new_point[0] == expected_point[0]
        assert new_point[1] == expected_point[1]

    def test_find_nearest_neighbor_from_candidates_returns_correctly_with_single_candidate(self, two_point_grid):
        candidates = {(2.5, 2.5)}
        # Point 1 has exact index (3, 3)
        (nn1, d1) = DistanceCalculator.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[0], candidates, two_point_grid.initialization_point, two_point_grid.cell_size)
        # Point 2 has exact index (7, 7)
        (nn2, d2) = DistanceCalculator.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[1], candidates, two_point_grid.initialization_point, two_point_grid.cell_size)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (2.5, 2.5))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (2.5, 2.5))

        assert (nn1, d1) == ((2.5, 2.5), expected_d1)
        assert (nn2, d2) == ((2.5, 2.5), expected_d2)

    def test_find_nearest_neighbor_from_candidates_returns_correctly_with_two_candidates(self, two_point_grid):
        candidates = {(2.5, 2.5), (5, 6)}
        # Point 1 has exact index (3, 3)
        (nn1, d1) = DistanceCalculator.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[0], candidates, two_point_grid.initialization_point, two_point_grid.cell_size)
        # Point 2 has exact index (7, 7)
        (nn2, d2) = DistanceCalculator.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[1], candidates, two_point_grid.initialization_point, two_point_grid.cell_size)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (2.5, 2.5))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (5, 6))

        assert (nn1, d1) == ((2.5, 2.5), expected_d1)
        assert (nn2, d2) == ((5, 6), expected_d2)

    def test_find_nearest_neighbor_from_candidates_returns_correctly_with_many_candidates(self, two_point_grid):
        candidates = {(2, 3), (3, 3), (5, 6), (7, 7)}
        # Point 1 has exact index (3, 3)
        (nn1, d1) = DistanceCalculator.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[0], candidates, two_point_grid.initialization_point, two_point_grid.cell_size)
        # Point 2 has exact index (7, 7)
        (nn2, d2) = DistanceCalculator.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[1], candidates, two_point_grid.initialization_point, two_point_grid.cell_size)

        expected_d1 = DistanceCalculator.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = DistanceCalculator.calculate_euclidian_distance_between_cells((7, 7), (7, 7))

        assert (nn1, d1) == ((3, 3), expected_d1)
        assert (nn2, d2) == ((7, 7), expected_d2)

    def test_calculated_euclidian_distance_between_cells(self):
        c1 = (0, 0)
        c2 = (1, 0)
        c3 = (0, 1)
        c4 = (1, 1)

        d_c1_c1 = DistanceCalculator.calculate_euclidian_distance_between_cells(c1, c1)
        d_c1_c2 = DistanceCalculator.calculate_euclidian_distance_between_cells(c1, c2)
        d_c1_c3 = DistanceCalculator.calculate_euclidian_distance_between_cells(c1, c3)
        d_c1_c4 = DistanceCalculator.calculate_euclidian_distance_between_cells(c1, c4)

        assert d_c1_c1 == 0
        assert d_c1_c2 == 1
        assert d_c1_c3 == 1
        assert d_c1_c4 == sqrt(2)

    def test_calculate_average_position(self):
        p1 = Point(2, 2)
        p2 = Point(6, 6)
        
        expected_avg_point = Point(4, 4)

        actual_avg_point = DistanceCalculator.calculate_average_position(p1, p2)

        assert expected_avg_point.get_coordinates() == actual_avg_point.get_coordinates()
