import pytest
from DTC.collection_utils import CollectionUtils

class TestCollectionUtils:

    @pytest.mark.parametrize("input_grid, output_distribution", 
        [
            ({(2,3) : [(2,3)]}, {1: 1}),                                # Single cell with single point
            ({(2,3) : [(2,3), (2.1, 3.1)]}, {2: 1}),                    # Single cell with two points
            ({(2,3) : [(2,3), (2.1, 3.1), (2.2, 3.2)]}, {3: 1})         # Single cell with three point
        ]
    )
    def test_point_distribution_for_cells_returns_correctly_with_single_cell(self, input_grid, output_distribution):
        assert CollectionUtils.get_point_distribution_for_cells(input_grid) == output_distribution

    @pytest.mark.parametrize("input_grid, output_distribution", 
        [
            ({(2,3) : [(2,3)], (4,5): [(4,5)]}, {1: 2}),                              # Two cells with single points
            ({(2,3) : [(2,3), (2.1, 3.1)], (4,5): [(4,5), (4.1, 5.1)]}, {2: 2}),      # Two cells with two points
            ({(2,3) : [(2,3), (2.1, 3.1)], (4,5): [(4,5)]}, {1: 1, 2: 1}),            # Two cells with different point counts
        ]
    )
    def test_point_distribution_for_cells_returns_correctly_with_two_cells(self, input_grid, output_distribution):
        assert CollectionUtils.get_point_distribution_for_cells(input_grid) == output_distribution

    @pytest.mark.parametrize("input_grid, output_distribution", 
        [
            ({(2,3) : [(2,3)], (4,5): [(4,5)], (6,7): [(6, 7)]}, {1: 3}),                                                  # Three cells with single points
            ({(2,3) : [(2,3)], (4,5): [(4,5)], (6,7): [(6,7), (6.1,7.1)]}, {1: 2, 2: 1}),                                  # Two cells with single points and single cell with two points
            ({(2,3) : [(2,3)], (4,5): [(4,5), (4.1,5.1)], (6,7): [(6,7), (6.1,7.1), (6.2,7.2)]}, {1: 1, 2: 1, 3: 1}),      # Three cells with different point counts
        ]
    )
    def test_point_distribution_for_cells_returns_correctly_with_three_cells(self, input_grid, output_distribution):
        assert CollectionUtils.get_point_distribution_for_cells(input_grid) == output_distribution

    @pytest.mark.parametrize("input_list, input_n, split_list_lengths", 
        [
            ([1, 2, 3, 4], 1, [4]),
            ([1, 2, 3, 4], 2, [2, 2]),
            ([1, 2, 3, 4], 4, [1, 1, 1, 1]),
            ([1], 4, [1, 0, 0, 0]),
            ({1, 2, 3, 4}, 1, [4]),
            ({1, 2, 3, 4}, 2, [2, 2]),
            ({1}, 4, [1, 0, 0, 0]),
            ({1: [2,2], 2: [1]}.values(), 1, [2]),
            ({1: [2,2], 2: [1]}.values(), 2, [1, 1]),
            ({1: [2,2], 2: [1]}.values(), 4, [1, 1, 0, 0])
        ]
    )
    def test_split_returns_correctly(self, input_list, input_n, split_list_lengths):
        split_lists = list(CollectionUtils.split(input_list, input_n))

        assert len(split_lists) == input_n
        for i in range(input_n):
            assert len(split_lists[i]) == split_list_lengths[i]

    @pytest.mark.parametrize("input_unsorted_collection, output_sorted_collection", 
        [
            ([(2, 1), (1, 2)], [(1, 2), (2, 1)]),
            ([(3, 1), (2, 1), (1, 1)], [(1, 1), (2, 1), (3, 1)]),
            ([(2, 2), (2, 1), (1, 2)], [(1, 2), (2, 1), (2, 2)]),
            ({(2, 1), (1, 2)}, [(1, 2), (2, 1)]),
            ({(3, 1), (2, 1), (1, 1)}, [(1, 1), (2, 1), (3, 1)]),
            ({(2, 2), (2, 1), (1, 2)}, [(1, 2), (2, 1), (2, 2)]),
        ]
    )
    def test_sort_collection_of_tuples_returns_correctly(self, input_unsorted_collection, output_sorted_collection):
        assert output_sorted_collection == CollectionUtils.sort_collection_of_tuples(input_unsorted_collection)

