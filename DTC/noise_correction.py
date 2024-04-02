from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory, Point
from geopy import distance

class NoiseCorrection:
    def __init__(self, gridsystem: GridSystem):
        self.gridsystem = gridsystem

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory):
        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = self.gridsystem.find_nearest_neighbor_from_candidates(point, self.gridsystem.route_skeleton)
            
            if dist >= self.gridsystem.safe_areas[nearest_anchor]:
                # Ensures that we do not try to clean first or last element. Should be improved!
                if i != 0 and i != len(trajectory.points) - 1:
                    self.correct_noisy_point(trajectory, i)

    def correct_noisy_point(self, trajectory: Trajectory, point_id: int):
        self.calculate_average_point(trajectory.points[point_id], trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        
        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, _ = self.gridsystem.find_nearest_neighbor_from_candidates(trajectory.points[point_id], self.gridsystem.route_skeleton) 
       
        if trajectory.points[point_id] is None:
            trajectory.points[point_id] = self.gridsystem.convert_cell_to_point(nearest_anchor)
        else:
            trajectory.points[point_id] = self.gridsystem.convert_cell_to_point(nearest_anchor, trajectory.points[point_id].timestamp)

    @staticmethod
    def calculate_average_point(p: Point, p_prev: Point, p_next: Point):
        p.longitude = (p_prev.longitude + p_next.longitude) / 2
        p.latitude = (p_prev.latitude + p_next.latitude) / 2

