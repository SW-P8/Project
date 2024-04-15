from DTC.construct_safe_area import SafeArea
from DTC.point import Point
from DTC.distance_calculator import DistanceCalculator

class Incremental:
    def __init__(self, safe_areas: dict[SafeArea]) -> None:
        self.safe_areas = safe_areas
        self.anchor_coords = self.__get_anchor_coordinate_set()
        self.new_cloud = None
        self.noisy_points = set()

    def incremental_refine(self, point: Point, initialization_point):
        if (not (len(self.anchor_coords) == len(self.safe_areas))):
            self.anchor_coords = self.__get_anchor_coordinate_set
        print(self.safe_areas.keys())
        (anchor, min_dist) = DistanceCalculator.find_nearest_neighbor_from_candidate_safe_areas(point, self.safe_areas.keys()) 
        if ((min_dist <= (self.safe_areas[anchor].radius))):
            self.safe_areas[anchor].increase_confidence()
        else:
            self.safe_areas[anchor].decrease_confidence()
            self.noisy_points.add(point)

    #Kind of hacky but our NN implementation uses sets instead of dicts so it has to be converted
    def __get_anchor_coordinate_set(self):
        cs = set()
        for sa in self.safe_areas.values():
            cs.add(sa.center)
        
        return cs





    

