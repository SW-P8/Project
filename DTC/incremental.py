from DTC.construct_safe_area import SafeArea, ConstructSafeArea
from DTC.trajectory import TrajectoryPointCloud
from DTC.distance_calculator import DistanceCalculator

class Incremental:
    def __init__(self, safe_areas: dict[SafeArea]) -> None:
        self.safe_areas = safe_areas
        self.anchor_coords = self.__get_anchor_coordinate_set()
        self.new_cloud = None
        self.noisy_points = set()

    def incremental_refine(self, new_cloud: TrajectoryPointCloud, initialization_point):
        if (not (len(self.anchor_coords) == len(self.safe_areas))):
            self.anchor_coords = self.__get_anchor_coordinate_set

        for trajectory in new_cloud.trajectories:
            for p in trajectory.points:
                (anchor, min_dist) = DistanceCalculator.find_nearest_neighbor_from_candidates(p, self.anchor_coords, initialization_point)
                if (min_dist <= self.safe_areas[anchor].radius):
                    #TODO: Bare lav increase og decrease af confidence nu lmao
                    pass
                else:
                    pass

    def __get_anchor_coordinate_set(self):
        cs = set()
        for sa in self.safe_areas.values():
            cs.add(sa.center)
        
        return cs





    

