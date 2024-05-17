from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator
from scipy.spatial import KDTree
from copy import deepcopy, copy
from onlinedtc.increment import update_safe_area
import time
import logging


logging.basicConfig(level=logging.INFO, filename='app.log')
logger = logging.getLogger(__name__)


class NoiseCorrection:
    def __init__(self, safe_areas, init_point, smoothed_main_route=set()):
        self.safe_areas = safe_areas
        self.safe_areas_keys_list = list(safe_areas.keys())
        self.safe_areas_keys_kd_tree = KDTree(self.safe_areas_keys_list)
        self.initialization_point = init_point
        self.smoothed_main_route = smoothed_main_route

    def noise_detection(self, trajectory: Trajectory, event_listener=None):
        labels_of_cleaned_points = []
        low_confidence_safe_areas = {}

        def update_function(data):
            low_confidence_safe_areas[data.anchor] = data

        checked_points = []
        discard_after_run = False

        self._check_for_noise_front_back(trajectory, labels_of_cleaned_points)

        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
            self.safe_areas[nearest_anchor].add_to_point_cloud(point)
            self.safe_areas[nearest_anchor].update_confidence(dist, point, update_function)

            checked_points.append((point, nearest_anchor, dist))

            self.safe_areas[nearest_anchor].add_to_point_cloud(deepcopy(point))
            if checked_points[i - 1][2] > self.safe_areas[checked_points[i - 1][1]].radius:
                if i > 1 and not self._check_consecutive_noise(i, checked_points):
                    labels_of_cleaned_points.append((point.noise))
                    self.correct_noisy_point(trajectory, i)

                else:
                    discard_after_run = True
                    break

        if len(low_confidence_safe_areas):
            if event_listener is not None:
                event_listener.emit()
            self._update_safe_areas(low_confidence_safe_areas)

        if discard_after_run:
            trajectory.points = None

        return labels_of_cleaned_points

    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(trajectory.points[point_id - 2], trajectory.points[point_id])
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
            avg_point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
        new_point = DistanceCalculator.convert_cell_to_point(self.initialization_point, nearest_anchor)
        trajectory.points[point_id - 1].set_coordinates(new_point)

    def _update_safe_areas(self, low_confidence_safe_areas):
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

    def _check_consecutive_noise(self, iterator, checked_points):
        _, nearest_neighbor, distance = checked_points[iterator]
        _, nearest_neighbor1, distance1 = checked_points[iterator - 1]
        _, nearest_neighbor2, distance2 = checked_points[iterator - 2]
        return (self.safe_areas[nearest_neighbor2].radius < distance2 and self.safe_areas[nearest_neighbor1].radius < distance1) or (self.safe_areas[nearest_neighbor1].radius < distance1 and self.safe_areas[nearest_neighbor].radius < distance)

    def _check_for_noise_front_back(self, trajectory: Trajectory, list_of_cleaned_points: list[bool]):
        # first check from front of trajectory if any noise-points can be removed.
        self._check_list_trajectory(trajectory, list_of_cleaned_points,)
        self._check_list_trajectory(trajectory, list_of_cleaned_points, True)

    def _check_list_trajectory(self, trajectory: Trajectory, list_of_cleaned_points: list[bool], fromBack: bool = False):
        if fromBack:
            iterator = len(trajectory.points) - 1
        else:
            iterator = 0
        while True:
            if not trajectory.points:
                return
            nearest_neighbor, distance = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                trajectory.points[iterator],
                self.safe_areas_keys_list,
                self.safe_areas_keys_kd_tree,
                self.initialization_point
            )
            if distance > self.safe_areas[nearest_neighbor].radius:
                self.safe_areas[nearest_neighbor].add_to_point_cloud(
                    copy(trajectory.points[iterator])
                )
                list_of_cleaned_points.append(
                    copy(trajectory.points[iterator].noise)
                )
                del trajectory.points[iterator]
                if fromBack:
                    iterator -= 1
            else:
                break
