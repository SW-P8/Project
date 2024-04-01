from DTC import gridsystem, trajectory
from geopy import distance

class NoiseCorrection:
    def __init__(self, gridsystem: gridsystem.GridSystem):
        self.gridsystem = gridsystem

    def noise_detection(self, trajectory):
        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = self.gridsystem.find_nearest_neighbor_from_candidates(point, self.gridsystem.route_skeleton)
            
            if dist >= self.gridsystem.safe_areas[nearest_anchor]:
                self.correct_noisy_point(trajectory, i)

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def correct_noisy_point(self, trajectory: trajectory.Trajectory, point_id: int):
        self.calculate_average_point(trajectory.points[point_id], trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        
        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, _ = self.gridsystem.find_nearest_neighbor_from_candidates(trajectory.points[point_id], self.gridsystem.route_skeleton) 
       
        trajectory.points[point_id] = self.gridsystem.convert_cell_to_point(nearest_anchor)

    @staticmethod
    def calculate_average_point(p: trajectory.Point, p_prev: trajectory.Point, p_next: trajectory.Point):
        p.longitude = (p_prev.longitude + p_next.longitude) / 2
        p.latitude = (p_prev.latitude + p_next.latitude) / 2

