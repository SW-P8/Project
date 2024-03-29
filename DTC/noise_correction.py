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
    def correct_noisy_point(self, trajectory, point_id: int):
        # Change noisy point p to be average of p-1 and p+1
        avg_point = self.calculate_average_point(trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        
        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, dist = self.gridsystem.find_nearest_neighbor_from_candidates(avg_point, self.gridsystem.route_skeleton) 
        
        # Make funciton in gridsystem that converts nearest_anchor (cell point to coordinate)

        # trajectory.points[point_id].set_coordinates(nearest_anchor)

    @staticmethod
    def calculate_average_point(p_prev: trajectory.Point, p_next: trajectory.Point) -> trajectory.Point:
        return trajectory.Point((p_prev.longitude + p_next.longitude) / 2, (p_prev.latitude + p_next.latitude) / 2)

