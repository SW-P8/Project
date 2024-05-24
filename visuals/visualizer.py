from datetime import datetime
import matplotlib.pyplot as plt
from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory, Point
from DTC.dtc_executor import DTCExecutor
from DTC.collection_utils import CollectionUtils


class Visualizer():
    def __init__(self, grid_system):
        self.grid_system = grid_system
        self.fig = plt.figure(figsize=(10, 5))

        # Create axes for point cloud
        self.pc_ax = self.fig.add_subplot(131)
        self.pc_ax.set_title('Point Cloud')

        # Create axes for main route
        self.mr_ax = self.fig.add_subplot(132)
        self.mr_ax.set_title('Main Route')

        # Create axes for route skeleton
        self.sk_ax = self.fig.add_subplot(133)
        self.sk_ax.set_title('Route skeleton')

    def visualize(self):
        self.draw_point_cloud()
        self.draw_main_route()
        self.draw_route_skeleton()
        self.draw_safe_area()
        plt.tight_layout()
        plt.show()

    def draw_point_cloud(self):
        for trajectory in self.grid_system.pc.trajectories:
            for point in trajectory.points:
                self.draw_point(self.pc_ax, point)

    def draw_main_route(self):
        for point in self.grid_system.main_route:
            self.draw_point(self.mr_ax, point)

    def draw_route_skeleton(self):
        print(self.grid_system.route_skeleton)
        for point in self.grid_system.route_skeleton:
            self.draw_point(self.sk_ax, point)

    def draw_safe_area(self):
        for anchor, radius in self.grid_system.safe_areas.items():
            self.draw_circle(self.sk_ax, anchor, radius)

    def draw_point(self, ax, point):
        if isinstance(point, Point):
            x, y = point.get_coordinates()
        else:
            x, y = point
        ax.scatter(x, y, c='blue', s=1)

    def draw_circle(self, ax, point, radius):
        if isinstance(point, Point):
            circle = plt.Circle(point.get_coordinates(),
                                radius, color='blue', fill=False)
        else:
            circle = plt.Circle(point, radius, color='blue', fill=False)
        ax.add_patch(circle)

    def draw_populated_cells(self):
        for cell in self.grid_system.populated_cells:
            self.draw_populated_cell(
                self.mr_ax, cell, self.grid_system.cell_size, self.grid_system.cell_size)

    def draw_populated_cell(self, ax, point, width, height):
        if isinstance(point, Point):
            rec = plt.Rectangle(point.get_coordinates(),
                                width, height, color='green')
        else:
            rec = plt.Rectangle(point, width, height, color='green')
        ax.add_patch(rec)

    @staticmethod
    def visualize_distribution_of_cells(distribution: dict):
        plt.bar(distribution.keys(), distribution.values(), color = "g")
        plt.show()

if __name__ == "__main__":
    dtc_executor = DTCExecutor()
    pc = dtc_executor.create_point_cloud_with_n_points(1000000)
    gs = GridSystem(pc)
    gs.create_grid_system()
    distribution = CollectionUtils.get_point_distribution_for_cells(gs.grid)
    Visualizer.visualize_distribution_of_cells(distribution)
