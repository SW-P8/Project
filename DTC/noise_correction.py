from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator
from scipy.spatial import KDTree
from onlinedtc.runner import update_safe_area
import time
import logging


logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)


class NoiseCorrection:
    def __init__(self, safe_areas, init_point, smoothed_main_route = set()):
        self.safe_areas = safe_areas
        self.safe_areas_keys_list = list(safe_areas.keys())
        self.safe_areas_keys_kd_tree = KDTree(self.safe_areas_keys_list)
        self.initialization_point = init_point
        self.smoothed_main_route = smoothed_main_route

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory: Trajectory):
        labels_of_cleaned_points = []
        low_confidence_safe_areas = {}

        def update_function(data):
            low_confidence_safe_areas[data.anchor] = data

        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
            self.safe_areas[nearest_anchor].add_to_point_cloud(point)
            self.safe_areas[nearest_anchor].update_confidence(dist, point, update_function)
            if dist > self.safe_areas[nearest_anchor].radius:
                # Ensures that we do not try to clean first or last element. Should be improved!
                if i != 0 and i != len(trajectory.points) - 1:
                    labels_of_cleaned_points.append((point.noise))
                    self.correct_noisy_point(trajectory, i)

        if len(low_confidence_safe_areas):
            self._update_safe_areas_thread(low_confidence_safe_areas)

        return labels_of_cleaned_points                   


    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
            avg_point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
        new_point = DistanceCalculator.convert_cell_to_point(self.initialization_point, nearest_anchor)
        trajectory.points[point_id].set_coordinates(new_point)
        avg_point = DistanceCalculator.calculate_average_position(
            trajectory.points[point_id - 1], trajectory.points[point_id + 1])

        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbor_from_candidates(
            avg_point, self.safe_areas.keys(), self.initialization_point)

        trajectory.points[point_id].set_coordinates(
            DistanceCalculator.convert_cell_to_point(self.initialization_point,
                                                     nearest_anchor))

    def _update_safe_areas_thread(self, low_confidence_safe_areas):
        start_time = time.time()

        updated_areas = {}
        for area in low_confidence_safe_areas.values():
            self.safe_areas.pop(area.anchor)
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Safe-areas: {low_confidence_safe_areas.keys()} have been removed in {duration: .2f} seconds")

        start_time = time.time()

        updated_areas = update_safe_area(low_confidence_safe_areas,
                                         self.initialization_point,
                                         self.smoothed_main_route)

        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Safe-areas updated in {duration: .2f} seconds")
        logger.info(f"Created the safe-areas: {updated_areas.keys()}")

        for safe_area in updated_areas.values():
            self.safe_areas[safe_area.anchor] = safe_area
