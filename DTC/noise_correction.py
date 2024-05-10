from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator
import logging
from scipy.spatial import KDTree

class NoiseCorrection:
    def __init__(self,safe_areas , init_point):
        self.safe_areas = safe_areas
        self.safe_areas_keys_list = list(safe_areas.keys())
        self.safe_areas_keys_kd_tree = KDTree(self.safe_areas_keys_list)
        self.initialization_point = init_point

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory: Trajectory):
        labels_of_cleaned_points = []
        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
            self.safe_areas[nearest_anchor].add_to_point_cloud(point)
            if dist > self.safe_areas[nearest_anchor].radius:
                # Ensures that we do not try to clean first or last element. Should be improved!
                if i != 0 and i != len(trajectory.points) - 1:
                    labels_of_cleaned_points.append((point.noise))
                    self.correct_noisy_point(trajectory, i)

        return trajectory, labels_of_cleaned_points                   


    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
            avg_point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
        new_point = DistanceCalculator.convert_cell_to_point(self.initialization_point, nearest_anchor)
        trajectory.points[point_id].set_coordinates(new_point)
