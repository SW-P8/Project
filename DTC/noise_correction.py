from DTC import gridsystem
from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator

class NoiseCorrection:
    def __init__(self, gridsystem: GridSystem):
        self.gridsystem = gridsystem

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory: Trajectory):
        noisy_points = []
        clear_points = []
        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbor_from_candidates(point, self.gridsystem.route_skeleton, self.gridsystem.initialization_point)
            for sa in self.gridsystem.safe_areas:
                if sa.anchor == nearest_anchor:
                   sa.PointsInSafeArea.append(point)
            
            if dist >= self.gridsystem.safe_areas[nearest_anchor].radius:
                # Ensures that we do not try to clean first or last element. Should be improved!
                if i != 0 and i != len(trajectory.points) - 1:
                    self.correct_noisy_point(trajectory, i)
                    

    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(trajectory.points[point_id - 1], trajectory.points[point_id + 1])
                
        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbor_from_candidates(avg_point, self.gridsystem.route_skeleton, self.gridsystem.initialization_point) 
       
        trajectory.points[point_id].set_coordinates(DistanceCalculator.convert_cell_to_point(self.gridsystem.initialization_point, nearest_anchor))

