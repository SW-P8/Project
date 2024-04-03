from DTC.distance_calculator import DistanceCalculator
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