from collections import defaultdict
from typing import Iterator
from DTC.trajectory import Trajectory

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
  
