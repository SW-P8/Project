from DTC import gridsystem, trajectory

class NoiseCorrection:
    def __init__(self, gridsystem: gridsystem.GridSystem):
        self.gridsystem = gridsystem

    def noise_detection(self, trajectory: trajectory.Trajectory):
        for point in trajectory.points:
            nearest_anchor, dist = self.gridsystem.find_nearest_neighbor_from_candidates(point, self.gridsystem.route_skeleton)
            
            if dist >= self.gridsystem.safe_areas[nearest_anchor]:
                self.noise_correction()

    def noise_correction(self):
        return NotImplemented



