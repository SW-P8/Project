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
            ({(2, 1): "something", (1, 2): "somethingelse"}.keys(), [(1, 2), (2, 1)])
        ]
    )
    def test_sort_collection_of_tuples_returns_correctly(self, input_unsorted_collection, output_sorted_collection):
        assert output_sorted_collection == CollectionUtils.sort_collection_of_tuples(input_unsorted_collection)

    @pytest.mark.parametrize("input_dict, input_key_subset, output_sub_dict",
        [
            ({(3, 3): "something", (4, 5): "somethingelse"}, {(3, 3), (4, 5)}, {(3, 3): "something", (4, 5): "somethingelse"}),
            ({(3, 3): "something", (4, 5): "somethingelse"}, {(3, 3)}, {(3, 3): "something"}),
            ({(3, 3): "something", (4, 5): "somethingelse", (5, 4): "somethingentirelydifferent"}, {(3, 3), (4, 5)}, {(3, 3): "something", (4, 5): "somethingelse"}),
        ]
    )
    def test_get_sub_dict_from_subset_of_keys_returns_correctly(self, input_dict, input_key_subset, output_sub_dict):
        assert output_sub_dict == CollectionUtils.get_sub_dict_from_subset_of_keys(input_dict, input_key_subset)

    @pytest.mark.parametrize("input_collection_of_tuples, output_ranges",
        [
            ([(1, 2), (3, 1)], (1, 1, 3, 2)),
            ([(1, 2)], (1, 2, 1, 2)),
            ([(1, 2), (2, 1), (3, 2), (2, 3)], (1, 1, 3, 3)),
            ({(1, 2)}, (1, 2, 1, 2)),
            ({(2, 1): "something", (1, 2): "somethingelse"}.keys(), (1, 1, 2, 2))
        ]                         
    )
    def test_get_min_max_with_padding_from_collection_of_tuples_returns_correctly_with_no_padding(self, input_collection_of_tuples, output_ranges):
        assert output_ranges == CollectionUtils.get_min_max_with_padding_from_collection_of_tuples(input_collection_of_tuples, 0)

    @pytest.mark.parametrize("input_collection_of_tuples, input_padding, output_ranges",
        [
            ([(1, 2), (3, 1)], 1, (0, 0, 4, 3)),
            ([(1, 2)], 1, (0, 1, 2, 3)),
            ([(1, 2), (2, 1), (3, 2), (2, 3)], 1, (0, 0, 4, 4)),
            ({(1, 2)}, 1, (0, 1, 2, 3)),
            ({(2, 1): "something", (1, 2): "somethingelse"}.keys(), 1, (0, 0, 3, 3))
        ]                         
    )
    def test_get_min_max_with_padding_from_collection_of_tuples_returns_correctly_with_padding(self, input_collection_of_tuples, input_padding, output_ranges):
        assert output_ranges == CollectionUtils.get_min_max_with_padding_from_collection_of_tuples(input_collection_of_tuples, input_padding)

    @pytest.mark.parametrize("input_collection_of_tuples, input_bounds, output_filtered_collection",
        [
            ([(1, 2)], (1, 1, 2, 2), [(1, 2)]),
            ([(1, 2), (0,0)], (1, 1, 2, 2), [(1, 2)]),
            ([(1, 2), (2, 1), (0, 0)], (1, 1, 2, 2), [(1, 2), (2, 1)]),
            ({(1, 2), (0,0)}, (1, 1, 2, 2), [(1, 2)]),
            ({(2, 1): "something", (0, 0): "somethingelse"}.keys(), (1, 1, 2, 2), [(2, 1)])
        ]
    )
    def test_get_tuples_within_bounds(self, input_collection_of_tuples, input_bounds, output_filtered_collection):
        assert output_filtered_collection == CollectionUtils.get_tuples_within_bounds(input_collection_of_tuples, input_bounds)
