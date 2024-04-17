from DTC.construct_safe_area import SafeArea
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator

class Incremental:
    def __init__(self, safe_areas: dict[SafeArea]) -> None:
        self.safe_areas = safe_areas
        self.noisy_points = set()

    def incremental_refine(self, point: Point, initialization_point):
        (anchor, min_dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(point, self.safe_areas.keys(), initialization_point) 
        self.safe_areas[anchor].update_confidence(min_dist)
        if ((min_dist > (self.safe_areas[anchor].radius))):
            self.noisy_points.add(point)
    

