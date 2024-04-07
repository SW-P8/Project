from rtree.index import Index
from DTC.distance_calculator import DistanceCalculator

class RTreeSkeletonExtractor:
    def __init__(self, main_route: Index):
        self.route_skeleton = set()

    def extract_route_skeleton(self, smooth_radius: int = 25, filtering_list_radius: int = 20, distance_interval: int = 20):
        smr = self.smooth_main_route(smooth_radius)
        cmr = self.filter_outliers_in_main_route(smr, filtering_list_radius)
        self.route_skeleton = self.sample_main_route(cmr, distance_interval)

    @staticmethod
    def smooth_main_route(main_route: Index, radius: int = 25) -> Index:
        smr = Index()
        already_inserted = set()
        for item in main_route.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True):
            print(item.id)
            x, y, _ , _ = item.bbox
            print(x, y)
            x_acc = 0
            y_acc = 0
            point_count = 0
            for inner_item in main_route.intersection((x - radius, y - radius, x + radius, y + radius), objects=True):
                x_n, y_n, _, _ = inner_item.bbox
                if DistanceCalculator.calculate_euclidian_distance_between_cells((x, y), (x_n, y_n)) <= radius:
                    x_acc += x_n + 0.5
                    y_acc += y_n + 0.5
                    point_count += 1
            x_avg = x_acc / point_count
            y_avg = y_acc / point_count
            if (x_avg, y_avg) not in already_inserted:
                smr.insert(item.id, (x_avg, y_avg, x_avg, y_avg))
                already_inserted.add((x_avg, y_avg))
        return smr

    def filter_outliers_in_main_route(self, smr: set, radius_prime: int = 20):
        tree = Index()
        
        for i, (x, y) in enumerate(smr):
            tree.insert(i, (x, y, x, y))  # Adding points to the R-tree
        
        cmr = set()
        for x, y in smr:
            nearby_points = tree.intersection((x - radius_prime, y - radius_prime, x + radius_prime, y + radius_prime), objects=True)
            if len(nearby_points) >= 0.01 * len(smr):
                cmr.add((x, y))
        return cmr

    def sample_main_route(self, cmr: set, distance_interval: int = 20):
        tree = Index()
        
        for i, (x, y) in enumerate(cmr):
            tree.insert(i, (x, y, x, y))  # Adding points to the R-tree
        
        rs = set()
        for x, y in cmr:
            nearby_points = tree.intersection((x - distance_interval, y - distance_interval, x + distance_interval, y + distance_interval), objects=True)
            if len(nearby_points) > 1:
                rs.add((x, y))
        return rs