import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from DTC.construct_main_route import ConstructMainRoute
from DTC.distance_calculator import DistanceCalculator
# Region -- Arrange Data
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

# Region -- Find density centers
grid_system = {}
density_centers = {}
for point in points:
    x, y = int(point[0]), int(point[1])
    if (x, y) not in grid_system:
        grid_system[(x, y)] = []
    grid_system[(x, y)].append(point)
for cell, cell_points in grid_system.items():
    density_centers[cell] = ConstructMainRoute.calculate_density_center(cell, grid_system)
    print(f"Cell {cell} - {cell_points} - {density_centers[cell]}")


# Region -- Insert data into figure
fig, ax = plt.subplots()

x, y = density_centers.pop((5, 5))
plt.scatter(*zip(*points), color='g', label='Point')
plt.scatter(x, y, color='red', label='Density center for current cell')
plt.scatter(*zip(*density_centers.values()), color='orange', label='Density center for other cells')
centerCell = plt.Rectangle((5, 5), 1, 1, color='green', alpha=0.375, label="Current cell")
neighborhood = plt.Rectangle((5 - DistanceCalculator.NEIGHBORHOOD_SIZE // 2, 5 - DistanceCalculator.NEIGHBORHOOD_SIZE // 2), DistanceCalculator.NEIGHBORHOOD_SIZE, DistanceCalculator.NEIGHBORHOOD_SIZE, color='red', fill=False, linewidth=2, label="Neighborhood")
ax.add_patch(centerCell)
ax.add_patch(neighborhood)

# Region -- Figure configuration
grid_ticks = np.arange(0, 100, 1)
ax.set_xticks(grid_ticks)
ax.set_yticks(grid_ticks)
ax.grid()
ax.set_axisbelow(True)
ax.set_aspect('equal')
plt.xlim(0, 10)
plt.ylim(0, 10)
plt.legend()
plt.show()