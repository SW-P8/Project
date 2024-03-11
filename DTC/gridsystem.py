import trajectory
from math import ceil, floor
from geopy import distance

class GridSystem:
    def __init__(self, pc: trajectory.TrajectoryPointCloud) -> None:
        self.pc = pc
        self.initialization_point = pc.get_shifted_min()
        self.cell_size = pc.cell_size

    def create_grid_system(self):
        (width, height) = self.pc.calculate_bounding_rectangle_area()
        width_cell_count = ceil(width / self.cell_size)
        height_cell_count = ceil(height / self.cell_size)

        # Initialize a 2d array containing empty lists 
        self.grid = [[list()]*height_cell_count for i in range(width_cell_count)]
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