from DTC import gridsystem, trajectory

class NoiseCorrection:
    def __init__(self, gridsystem: gridsystem.GridSystem):
        self.gridsystem = gridsystem

    def noise_detection(self, trajectory):
        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = self.gridsystem.find_nearest_neighbor_from_candidates(point, self.gridsystem.route_skeleton)
            
            if dist >= self.gridsystem.safe_areas[nearest_anchor]:
                self.noise_correction(trajectory, i)

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_correction(self, trajectory, point_id: int):
        # Change noisy point p to be average of p-1 and p+1
        average_point = self.calculate_average_point(trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        
        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, dist = self.gridsystem.find_nearest_neighbor_from_candidates(average_point, self.gridsystem.route_skeleton)
        return nearest_anchor

    @staticmethod
    def calculate_average_point(p1, p2):
        return (p1 + p2) / 2

