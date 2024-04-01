import pytest
from DTC.analyzer import Analyzer

class TestAnalyzer:

    @pytest.mark.parametrize("input_grid, output_distribution", 
        [
            ({(2,3) : [(2,3)]}, {1: 1}),                                # Single cell with single point
            ({(2,3) : [(2,3), (2.1, 3.1)]}, {2: 1}),                    # Single cell with two points
            ({(2,3) : [(2,3), (2.1, 3.1), (2.2, 3.2)]}, {3: 1})         # Single cell with three point
        ]
    )
    def test_point_distribution_for_cells_returns_correctly_with_single_cell(self, input_grid, output_distribution):
        assert Analyzer.get_point_distribution_for_cells(input_grid) == output_distribution

    @pytest.mark.parametrize("input_grid, output_distribution", 
        [
            ({(2,3) : [(2,3)], (4,5): [(4,5)]}, {1: 2}),                              # Two cells with single points
            ({(2,3) : [(2,3), (2.1, 3.1)], (4,5): [(4,5), (4.1, 5.1)]}, {2: 2}),      # Two cells with two points
            ({(2,3) : [(2,3), (2.1, 3.1)], (4,5): [(4,5)]}, {1: 1, 2: 1}),            # Two cells with different point counts
        ]
    )
    def test_point_distribution_for_cells_returns_correctly_with_two_cells(self, input_grid, output_distribution):
        assert Analyzer.get_point_distribution_for_cells(input_grid) == output_distribution

    @pytest.mark.parametrize("input_grid, output_distribution", 
        [
            ({(2,3) : [(2,3)], (4,5): [(4,5)], (6,7): [(6, 7)]}, {1: 3}),                                                  # Three cells with single points
            ({(2,3) : [(2,3)], (4,5): [(4,5)], (6,7): [(6,7), (6.1,7.1)]}, {1: 2, 2: 1}),                                  # Two cells with single points and single cell with two points
            ({(2,3) : [(2,3)], (4,5): [(4,5), (4.1,5.1)], (6,7): [(6,7), (6.1,7.1), (6.2,7.2)]}, {1: 1, 2: 1, 3: 1}),      # Three cells with different point counts
        ]
    )
    def test_point_distribution_for_cells_returns_correctly_with_three_cells(self, input_grid, output_distribution):
        assert Analyzer.get_point_distribution_for_cells(input_grid) == output_distribution