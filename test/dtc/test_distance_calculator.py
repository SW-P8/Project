from DTC.distance_calculator import DistanceCalculator
from DTC.point import Point
from math import sqrt

class TestDistanceCalculator:
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
