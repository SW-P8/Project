from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator
from concurrent.futures import ThreadPoolExecutor
from onlinedtc.runner import update_safe_area


class NoiseCorrection:
    def __init__(self, safe_areas, route_skeleton, init_point):
        self.route_skeleton = route_skeleton
        self.safe_areas = safe_areas
        self.initialization_point = init_point

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory: Trajectory):
        low_confidence_safe_areas = {}

        def update_function(data):
            low_confidence_safe_areas[data.anchor] = data

        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbor_from_candidates(
                point, self.safe_areas.keys(), self.initialization_point)
            self.safe_areas[nearest_anchor].add_to_point_cloud(point)
            self.safe_areas[nearest_anchor].update_confidence(dist, point, update_function)
            if dist >= self.safe_areas[nearest_anchor].radius:
                # Ensures that we do not try to clean first or last element. Should be improved!
                if i > 1 and i != len(trajectory.points) - 1:
                    self.correct_noisy_point(trajectory, i)

        if len(low_confidence_safe_areas):
            self._update_safe_areas_thread(low_confidence_safe_areas)
        
        print("")

    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(
            trajectory.points[point_id - 1], trajectory.points[point_id + 1])

        # Calculate noisy point to be the center of nearest anchor.
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbor_from_candidates(
            avg_point, self.route_skeleton, self.initialization_point)

        trajectory.points[point_id].set_coordinates(
            DistanceCalculator.convert_cell_to_point(self.initialization_point, nearest_anchor))
        
    def _update_safe_areas_thread(self, low_confidence_safe_areas):
        updated_areas = []
        with ThreadPoolExecutor() as executor:
            for area in low_confidence_safe_areas.values():
                self.safe_areas.pop(area.anchor)
                updated_area = executor.submit(self.update_safe_area, area).result()
                self.safe_areas[updated_area.anchor] = updated_area

        return updated_areas

    
    def update_safe_area(self, safe_area):
        return update_safe_area(safe_area, self.safe_areas, self.initialization_point, self.route_skeleton)
