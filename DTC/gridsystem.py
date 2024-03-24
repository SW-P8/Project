from DTC import trajectory
from math import ceil, floor, sqrt
from geopy import distance

class GridSystem:
    def __init__(self, pc: trajectory.TrajectoryPointCloud) -> None:
        self.pc = pc
        self.initialization_point = pc.get_shifted_min()
        self.cell_size = pc.cell_size
        self.neighborhood_size = pc.neighborhood_size

    def create_grid_system(self):
        (width, height) = self.pc.calculate_bounding_rectangle_area()
        width_cell_count = ceil(width / self.cell_size)
        height_cell_count = ceil(height / self.cell_size)

        # Initialize a 2d array containing empty lists 
        self.grid = [[[] for j in range(height_cell_count)] for i in range(width_cell_count)]
        self.populated_cells = set()
        
        # Fill grid with points
        for trajectory in self.pc.trajectories:
            for point in trajectory.points:
                (x,y) = self.calculate_index_for_point(point)
                self.grid[x][y].append(point)
                self.populated_cells.add((x,y))

    # TODO: Determine if you want to round within some treshold (shifting may not result in precise distances)
    def calculate_index_for_point(self, point: trajectory.Point):
        # Calculate x index
        x_offset = distance.distance((self.initialization_point[1], self.initialization_point[0]), (self.initialization_point[1], point.longitude)).meters
        x_coordinate = floor(x_offset / self.cell_size) - 1

        # Calculate y index
        y_offset = distance.distance((self.initialization_point[1], self.initialization_point[0]), (point.latitude ,self.initialization_point[0])).meters
        y_coordinate = floor(y_offset / self.cell_size) - 1

        return (x_coordinate, y_coordinate)
    
    def extract_main_route(self, distance_scale: float = 0.2):
        self.main_route = set()

        if distance_scale >= 0.5:
            raise ValueError("distance scale must be less than neighborhood size divided by 2")
        distance_threshold = distance_scale * self.neighborhood_size

        for cell in self.populated_cells:
            density_center = self.calculate_density_center(cell)

            if self.calculate_euclidian_distance_between_cells(cell, density_center) < distance_threshold:
                self.main_route.add(cell)

    def calculate_density_center(self, index):
        (x, y) = index
        l = floor(self.neighborhood_size / 2)
        point_count = 0
        (x_sum, y_sum) = (0, 0)
 
        for i in range(x - l, x + l + 1):
            for j in range(y - l, y + l + 1):
                if self.grid[i][j]:
                    cardinality = len(self.grid[i][j])
                    x_sum += cardinality * i
                    y_sum += cardinality * j
                    point_count += cardinality

        if x_sum != 0:
            x_sum /= point_count

        if y_sum != 0:
            y_sum /= point_count

        return (x_sum, y_sum)
    
    def extract_route_skeleton(self):
        smr = self.smooth_main_route()
        cmr = self.filter_outliers_in_main_route(smr)
        self.route_skeleton = self.sample_main_route(cmr)
        
    def smooth_main_route(self, radius: int = 25) -> set:
        smr = set()
        for (x1, y1) in self.main_route:
            ns = {(x2, y2) for (x2, y2) in self.main_route if self.calculate_euclidian_distance_between_cells((x1 + 0.5, y1 + 0.5), (x2 + 0.5, y2 + 0.5)) <= radius}
            x_sum = sum(x for x, _ in ns) + len(ns) * 0.5
            y_sum = sum(y for _, y in ns) + len(ns) * 0.5

            if x_sum != 0:
                x_sum /= len(ns)

            if y_sum != 0:
                y_sum /= len(ns)            
            smr.add((x_sum, y_sum))
        return smr
    
    def filter_outliers_in_main_route(self, smr: set, radius_prime: int = 20):
        cmr = set()
        for (x1, y1) in smr:
            targets = {(x2, y2) for (x2, y2) in smr if self.calculate_euclidian_distance_between_cells((x1, y1), (x2, y2)) <= radius_prime}
            if len(targets) >= 0.01 * len(smr):
                cmr.add((x1, y1))
        return cmr
    
    def sample_main_route(self, cmr: set, distance_interval: int = 20):
        rs = set()
        for c1 in cmr:
            targets = {c2 for c2 in cmr if self.calculate_euclidian_distance_between_cells(c1, c2) <= distance_interval}
            # targets should be greater than 1 to take self into account
            if len(targets) > 1:
                rs.add(c1)
        return rs
    
    @staticmethod
    def calculate_euclidian_distance_between_cells(cell1, cell2):
        (x_1, y_1) = cell1
        (x_2, y_2) = cell2
        return sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)
