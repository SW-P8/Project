import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from DTC.construct_main_route import ConstructMainRoute
points = [
    (3.1, 3.1),
    (3.8, 3.8),
    (4.5, 4.2),
    (4.5, 4.8),
    (5.1, 5.1),
    (5.3, 5.3),
    (5.1, 5.3),
    (5.3, 5.1),
    (6.2, 5.1),
    (6.8, 5.1),
    (6.2, 5.2),
    (6.8, 5.2),
    (7.2, 4.8),
    (7.2, 4.4),
    (7.6, 4.4),
    (8.8, 3.2)
]

grid_system = {}
density_centers = []

for point in points:
    x, y = int(point[0]), int(point[1])
    if (x, y) not in grid_system:
        grid_system[(x, y)] = []
    grid_system[(x, y)].append(point)
for cell, cell_points in grid_system.items():
    density_center = ConstructMainRoute.calculate_density_center(cell, grid_system)
    density_centers.append(density_center)
    print(f"Cell {cell} - {cell_points} - {density_center}")

fig, ax = plt.subplots()
grid_ticks = np.arange(0, 100, 1)
ax.set_xticks(grid_ticks)
ax.set_yticks(grid_ticks)
ax.grid()

plt.scatter(*zip(*points), color='g')
plt.scatter(*zip(*density_centers), color='red')


centerCell = plt.Rectangle((5, 5), 1, 1, color='green', alpha=0.375)
neighborhood = plt.Rectangle((1,1), 9, 9, color='red', fill=False)
ax.add_patch(centerCell)
ax.add_patch(neighborhood)
plt.show()