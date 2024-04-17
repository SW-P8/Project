from collections import defaultdict
from typing import Iterator
from operator import itemgetter
class CollectionUtils:
    @staticmethod
    def get_point_distribution_for_cells(grid: dict):
        # Use defaultdict(int) to simplify the counting process
        distribution = defaultdict(int)
        
        for points in grid.values():
            cell_cardinality = len(points)
            distribution[cell_cardinality] += 1

        return dict(sorted(distribution.items()))
    
    @staticmethod
    def split(a, n) -> Iterator[list]:
        a = list(a)
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
    
    @staticmethod
    def sort_collection_of_tuples(collection_of_tuples) -> list:
        return sorted(collection_of_tuples, key=(itemgetter(0,1)))
    
    @staticmethod
    def get_sub_dict_from_subset_of_keys(d: dict, keys) -> dict:
        return {key:d[key] for key in keys}

    @staticmethod
    def get_tuples_within_bounds(collection_of_tuples, bounds: tuple):
        return [(x, y) for x, y in collection_of_tuples if bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]]

    @staticmethod
    def get_min_max_with_padding_from_collection_of_tuples(collection_of_tuples, padding) -> tuple:
        min_x = min(collection_of_tuples, key=itemgetter(0))[0] - padding
        max_x = max(collection_of_tuples, key=itemgetter(0))[0] + padding
        min_y = min(collection_of_tuples, key=itemgetter(1))[1] - padding
        max_y = max(collection_of_tuples, key=itemgetter(1))[1] + padding

        return (min_x, min_y, max_x, max_y)
