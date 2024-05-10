from DTC import gridsystem, route_skeleton
from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory
from DTC.distance_calculator import DistanceCalculator
import copy
import logging
from geopy.distance import geodesic
from pyproj import Proj, transform

logging.basicConfig(level=logging.DEBUG)


class NoiseCorrection:
    def __init__(self,safe_areas , init_point):
        self.route_skeleton = route_skeleton
        self.safe_areas = safe_areas
        self.initialization_point = init_point
        self.noisy_points = []

    # TODO decide how to handle if p-1 or p+1 is also noise, such that we do not correct noise with noise.
    def noise_detection(self, trajectory: Trajectory):
        for i, point in enumerate(trajectory.points):
            nearest_anchor, dist = DistanceCalculator.find_nearest_neighbor_from_candidates(point, self.safe_areas.keys(), self.initialization_point)
            self.safe_areas[nearest_anchor].add_to_point_cloud(point)
            if dist >= self.safe_areas[nearest_anchor].radius:
                # Ensures that we do not try to clean first or last element. Should be improved!
                if i != 0 and i != len(trajectory.points) - 1:
                    logging.debug(f"Nearest anchor: {nearest_anchor}, Distance: {dist}")
                    self.noisy_points.append((point.noise))
                    self.correct_noisy_point(trajectory, i)
                    nearest_anchor, new_dist = DistanceCalculator.find_nearest_neighbor_from_candidates(trajectory.points[i], self.safe_areas.keys(), self.initialization_point)
                    logging.debug(f"Nearest anchor: {nearest_anchor}, Distance: {new_dist}")
                    logging.debug(f"radius of nearest anchor {self.safe_areas[nearest_anchor].radius}")
                    logging.debug(f"DEBUG: index for corrected point {DistanceCalculator.calculate_exact_index_for_point(point, self.initialization_point)}")
                    if new_dist < self.safe_areas[nearest_anchor].radius:
                        #logging.debug(f"Point {i} successfully corrected.")
                        pass
                    else:
                        logging.debug(f"Correction failed for point {i}, distance {new_dist}")
        return trajectory, self.noisy_points                    


    def correct_noisy_point(self, trajectory: Trajectory, point_id: int) -> None:
        avg_point = DistanceCalculator.calculate_average_position(trajectory.points[point_id - 1], trajectory.points[point_id + 1])
        nearest_anchor, _ = DistanceCalculator.find_nearest_neighbor_from_candidates(avg_point, self.safe_areas.keys(), self.initialization_point)
        #new_point = self.convert_cell_to_point_2(self.initialization_point, nearest_anchor)
        #grid_proj, geo_proj = self.setup_grid_to_geo_transformer(self.initialization_point[1], self.initialization_point[0])
        #new_point = self.convert_grid_to_geo(nearest_anchor[1], nearest_anchor[0], grid_proj, geo_proj)
        #new_point_switched = (new_point[1], new_point[0])
        new_point = DistanceCalculator.convert_cell_to_point(self.initialization_point, nearest_anchor)
        logging.debug(f"Old point {trajectory.points[point_id].get_coordinates()}")
        trajectory.points[point_id].set_coordinates(new_point)
        logging.debug(f"{nearest_anchor}")
        logging.debug(f"Corrected point {point_id} to new coordinates {new_point}")
        
    def setup_grid_to_geo_transformer(self, origin_latitude, origin_longitude):
        grid_proj = Proj(proj='tmerc', lat_0=origin_latitude, lon_0=origin_longitude, k=1, x_0=0, y_0=0, ellps='WGS84', units='m')
        # WGS84 Proj instance for lat/long
        geo_proj = Proj(proj='latlong', datum='WGS84')

        return grid_proj, geo_proj

    def convert_grid_to_geo(self, x, y, grid_proj, geo_proj):
        # Transform from grid coordinates to geographic coordinates
        lat, lon = transform(grid_proj, geo_proj, x, y)
        return lon, lat
