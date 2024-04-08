from rtree.index import Index
from DTC.distance_calculator import DistanceCalculator

class RTreeSkeletonExtractor:
    @staticmethod
    def extract_route_skeleton(main_route: Index, smooth_radius: int = 25, filtering_list_radius: int = 20, distance_interval: int = 20):
        smr = RTreeSkeletonExtractor.smooth_main_route(main_route, smooth_radius)
        cmr = RTreeSkeletonExtractor.filter_outliers_in_main_route(smr, filtering_list_radius)
        return RTreeSkeletonExtractor.sample_main_route(cmr, distance_interval)

    @staticmethod
    def smooth_main_route(main_route: Index, radius: int = 25) -> Index:
        smr = Index()
        already_inserted = set()
        
        for item in main_route.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True):
            x, y, _ , _ = item.bbox
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

    @staticmethod
    def filter_outliers_in_main_route(smr: Index, radius_prime: int = 20) -> Index:
        cmr = Index()
        smr_size = len(list(smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True)))
        for item in smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True):
            x, y, _ , _ = item.bbox
            point_count = 0

            for inner_item in smr.intersection((x - radius_prime, y - radius_prime, x + radius_prime, y + radius_prime), objects=True):
                x_n, y_n, _, _ = inner_item.bbox
                if DistanceCalculator.calculate_euclidian_distance_between_cells((x, y), (x_n, y_n)) <= radius_prime:
                    point_count += 1

            if point_count >= 0.01 * smr_size:
                cmr.insert(item.id, (x, y, x, y))

        return cmr        


    def sample_main_route(self, cmr: Index, distance_interval: int = 20) -> Index:
        tree = Index()
        
        for i, (x, y) in enumerate(cmr):
            tree.insert(i, (x, y, x, y))  # Adding points to the R-tree
        
        rs = set()
        for x, y in cmr:
            nearby_points = tree.intersection((x - distance_interval, y - distance_interval, x + distance_interval, y + distance_interval), objects=True)
            if len(nearby_points) > 1:
                rs.add((x, y))
        return rs