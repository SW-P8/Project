from distance_calculator import DistanceCalculator

class RouteSkeleton:
    def __init__(self, main_route) -> None:
        self.main_route = main_route
    
    
        
    def smooth_main_route(self, radius: int = 25) -> set:
        smr = set()
        for (x1, y1) in self.main_route:
            ns = {(x2, y2) for (x2, y2) in self.main_route if DistanceCalculator.calculate_euclidian_distance_between_cells((x1 + 0.5, y1 + 0.5), (x2 + 0.5, y2 + 0.5)) <= radius}
            x_sum = sum(x for x, _ in ns) + len(ns) * 0.5
            y_sum = sum(y for _, y in ns) + len(ns) * 0.5

            if x_sum != 0:
                x_sum /= len(ns)

            if y_sum != 0:
                y_sum /= len(ns)
            smr.add((x_sum, y_sum))
        return smr
    
    def filter_outliers_in_main_route(self, smr: set, radius_prime: int = 20):
        cmr = set()
        for (x1, y1) in smr:
            targets = {(x2, y2) for (x2, y2) in smr if DistanceCalculator.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= radius_prime}
            if len(targets) >= 0.01 * len(smr):
                cmr.add((x1, y1))
        return cmr
    
    def sample_main_route(self, cmr: set, distance_interval: int = 20):
        rs = set()
        for c1 in cmr:
            targets = {c2 for c2 in cmr if DistanceCalculator.calculate_euclidian_distance_between_cells(c1, c2) <= distance_interval}
            # targets should be greater than 1 to take self into account
            if len(targets) > 1:
                rs.add(c1)
        return rs
    


class RouteSkeletonWrapper:
    def __init__(self) -> None:
        pass



