from math import sqrt
from DTC.safe_area import SafeArea
from DTC.distance_calculator import DistanceCalculator

class ConstructSafeArea:
    @staticmethod
    def construct_safe_areas(route_skeleton: set, grid: dict, populated_cells: set, decrease_factor: float, initialization_point) -> dict:
        cs = ConstructSafeArea._create_cover_sets(route_skeleton, grid, populated_cells, initialization_point)

        safe_areas = dict()

        for anchor in route_skeleton:
            safe_areas[anchor] = SafeArea(cs[anchor], anchor, decrease_factor)

        return safe_areas

    @staticmethod
    def _create_cover_sets(route_skeleton: set, grid: dict, populated_cells: set, initialization_point: tuple, find_candidate_algorithm = None) -> dict:
        if find_candidate_algorithm is None:
            find_candidate_algorithm = ConstructSafeArea._find_candidate_nearest_neighbors
        
        cs = dict()
        # Initialize dictionary with a key for each anchor and an empty set for each
        for anchor in route_skeleton:
            cs[anchor] = set()

        # Assign points to their nearest anchor
        for (x, y) in populated_cells:
            candidates = find_candidate_algorithm(route_skeleton, (x + 0.5, y + 0.5))
            for point in grid[(x, y)]:
                (anchor, dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(point, candidates, initialization_point)
                cs[anchor].add((point, dist))

        return cs

    @staticmethod
    def _find_candidate_nearest_neighbors(route_skeleton: set, cell: tuple) -> dict:
        min_dist = float("inf")
        candidates = set()
        distance_to_corner_of_cell = sqrt(0.5 ** 2 + 0.5 ** 2)
        
        for anchor in route_skeleton:
            dist = DistanceCalculator.calculate_euclidian_distance_between_cells(cell, anchor)
            if dist <= min_dist + distance_to_corner_of_cell:
                if dist < min_dist:
                    min_dist = dist
                candidates.add((anchor, dist))

        return {a for a, d in candidates if d <= min_dist + distance_to_corner_of_cell}

