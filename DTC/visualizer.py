from datetime import datetime
import matplotlib.pyplot as plt
from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory, Point
from DTC.dtc_executor import DTCExecutor

class Visualizer():
    def __init__(self, grid_system):
        self.grid_system = grid_system
        self.fig, self.ax = plt.subplots()

    def visualize(self):
        self.draw_main_route()
        self.draw_populated_cells()
        self.ax.legend(["point"])
        plt.show()
    
    def draw_point_cloud(self):
        for trajectory in self.grid_system.pc.trajectories:
            for point in trajectory.points:
                self.draw_point(point)

    def draw_main_route(self):
        for point in self.grid_system.main_route:
            self.draw_point(point)

    def draw_point(self, point):
        if isinstance(point, Point):
            x, y = point.get_coordinates()
        else:
            x, y = point
        self.ax.scatter(x, y, c='blue', s=1)

    def draw_safe_area(self, point, radius):
        if isinstance(point, Point):
            circle = plt.Circle(point.get_coordinates(), radius, color='blue', fill=False)
        else:
            circle = plt.Circle(point, radius, color='blue', fill=False)
        self.ax.add_patch(circle)

    def draw_populated_cells(self):
        for cell in self.grid_system.populated_cells:
            self.draw_populated_cell(cell, self.grid_system.cell_size, self.grid_system.cell_size)

    def draw_populated_cell(self, point, width, height):
        if isinstance(point, Point):
            rec = plt.Rectangle(point.get_coordinates(), width, height, color='green')
        else:
            rec = plt.Rectangle(point, width, height, color='green')
        self.ax.add_patch(rec)

if __name__ == "__main__":
    dtc_executor = DTCExecutor(True)
    gs = dtc_executor.execute_dtc_with_n_points(2000)
    visualizer = Visualizer(gs)
    visualizer.visualize()
