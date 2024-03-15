import trajectory
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

        if d >= 0.5:
            raise ValueError("d must be less than neighborhood size divided by 2")
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
    
    @staticmethod
    def calculate_euclidian_distance_between_cells(cell1, cell2):
        (x_1, y_1) = cell1
        (x_2, y_2) = cell2
        return sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2)
