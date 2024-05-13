from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator
from scipy.spatial import KDTree
from copy import deepcopy

class NoiseCorrection:
    def __init__(self,safe_areas, init_point):
        self.safe_areas = safe_areas
        self.safe_areas_keys_list = list(safe_areas.keys())
        self.safe_areas_keys_kd_tree = KDTree(self.safe_areas_keys_list)
        self.initialization_point = init_point

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory: Trajectory):
        labels_of_cleaned_points = []
        checked_points = []
        discard_after_run = False

        self._check_for_noise_front_back(trajectory, labels_of_cleaned_points)

        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)

            checked_points.append((point, nearest_anchor, dist))

            self.safe_areas[nearest_anchor].add_to_point_cloud(deepcopy(point))
            if checked_points[i - 1][2] > self.safe_areas[checked_points[i - 1][1]].radius:
                if i > 1 and self._check_consecutive_noise(i, checked_points):
                    discard_after_run = True
                    break

                if i > 1:
                    print("cleaned")
                    labels_of_cleaned_points.append((point.noise))
                    self.correct_noisy_point(trajectory, i)

        if discard_after_run:
            trajectory.points = None

        return labels_of_cleaned_points

    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(trajectory.points[point_id - 2], trajectory.points[point_id])
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
            avg_point, self.safe_areas_keys_list, self.safe_areas_keys_kd_tree, self.initialization_point)
        new_point = DistanceCalculator.convert_cell_to_point(self.initialization_point, nearest_anchor)
        trajectory.points[point_id -1].set_coordinates(new_point)

    def _check_consecutive_noise(self, iterator, checked_points):
        _, nearest_neighbor, distance = checked_points[iterator]
        _, nearest_neighbor1, distance1 = checked_points[iterator - 1]
        _, nearest_neighbor2, distance2 = checked_points[iterator - 2]

        print(distance, distance1, distance2)

        if (self.safe_areas[nearest_neighbor2].radius < distance2 and self.safe_areas[nearest_neighbor1].radius < distance1) or (self.safe_areas[nearest_neighbor1].radius < distance1 and self.safe_areas[nearest_neighbor].radius < distance):
            return True

        return False

    def _check_for_noise_front_back(self, trajectory: Trajectory, list_of_cleaned_points: list[bool]):
        iterator = 0

        # first check from front of trajectory if any noise-points can be removed.
        while iterator < len(trajectory.points):
            nearest_neighbor, distance = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                trajectory.points[iterator],
                self.safe_areas_keys_list,
                self.safe_areas_keys_kd_tree,
                self.initialization_point)
            if distance > self.safe_areas[nearest_neighbor].radius:
                self.safe_areas[nearest_neighbor].add_to_point_cloud(
                    deepcopy(trajectory.points[iterator]))
                list_of_cleaned_points.append(trajectory.points[iterator].noise)
                del trajectory.points[iterator]
            else:
                break
            iterator += 1

        # next check from the back.
        iterator = len(trajectory.points) - 1
        while iterator >= 0:
            nearest_neighbor, distance = DistanceCalculator.find_nearest_neighbour_from_candidates_with_kd_tree(
                trajectory.points[iterator],
                self.safe_areas_keys_list,
                self.safe_areas_keys_kd_tree,
                self.initialization_point
            )
            if distance > self.safe_areas[nearest_neighbor].radius:
                self.safe_areas[nearest_neighbor].add_to_point_cloud(
                    deepcopy(trajectory.points[iterator]))
                list_of_cleaned_points.append(
                    trajectory.points[iterator].noise)
                del trajectory.points[iterator]
            else:
                break
            iterator += 1
