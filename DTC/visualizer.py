from datetime import datetime
import matplotlib.pyplot as plt
from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory, Point

class Visualizer():
    def __init__(self, grid_system):
        self.grid_system = grid_system
        self.fig, self.ax = plt.subplots()

    def visualize(self):
        for trajectory in self.grid_system.pc.trajectories:
            for point in trajectory.points:
                self.draw_point(point)
                self.draw_safe_area(point, 3)
        self.ax.legend(["point"])
        plt.show()

    def draw_point(self, point):
        x, y = point.get_coordinates()
        self.ax.scatter(x, y, c='blue')

    def draw_safe_area(self, point, radius):
        circle = plt.Circle(point.get_coordinates(), radius, color='blue', fill=False)
        self.ax.add_patch(circle)


if __name__ == "__main__":
    print("hello world")

    t = Trajectory()
    time = datetime(2024, 1, 1, 1, 1, 1)
    t.add_point(0,0,time)
    t.add_point(15, 20, time)
    t.add_point(30, 30, time)
    t.add_point(37, 42, time)
    point_cloud = TrajectoryPointCloud()
    point_cloud.add_trajectory(t)
    grid_system = GridSystem(point_cloud)
    v = Visualizer(grid_system)
    v.visualize()
