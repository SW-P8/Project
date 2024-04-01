from collections import defaultdict

class Analyzer:
    @staticmethod
    def get_point_distribution_for_cells(grid: dict):
        # Use defaultdict(int) to simplify the counting process
        distribution = defaultdict(int)
        
        for points in grid.values():
            cell_cardinality = len(points)
            distribution[cell_cardinality] += 1

        return distribution
