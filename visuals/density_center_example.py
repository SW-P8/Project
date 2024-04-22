import numpy as np
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
    (5.1, 5.3),
    (5.3, 5.1),
    (5.3, 5.3),
    (6.2, 5.1),
    (6.2, 5.2),
    (6.8, 5.1),
    (6.8, 5.2),
    (7.2, 4.4),
    (7.2, 4.8),
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
    density_centers[cell] = ConstructMainRoute.calculate_density_center(
        cell, grid_system)

main_route = ConstructMainRoute.extract_main_route(grid_system)

# Region -- Insert data into figures
fig_all, ax_dc = plt.subplots()
fig_main, ax_mr = plt.subplots()

# Plot all elements in the first figure
x, y = density_centers.pop((5, 5))
ax_dc.scatter(*zip(*points), color='g', label='Point')
ax_dc.scatter(*zip(*density_centers.values()), color='orange',
               label='Density center for other cells')
ax_dc.scatter(x, y, color='red', label='Density center for current cell')
ax_dc.add_patch(plt.Rectangle((5, 5), 1, 1, color='green',
                               alpha=0.375, label="Current cell"))
ax_dc.add_patch(plt.Rectangle((5 - DistanceCalculator.NEIGHBORHOOD_SIZE // 2, 5 - DistanceCalculator.NEIGHBORHOOD_SIZE // 2),
                               DistanceCalculator.NEIGHBORHOOD_SIZE, DistanceCalculator.NEIGHBORHOOD_SIZE,
                               color='green', alpha=0.1, fill=True, linewidth=2, label="Neighborhood"))

# Plot only the main route in the second figure
ax_mr.scatter(*zip(*points), color='g', label='Point')
for i, cell in enumerate(main_route):
    if i == 0:
        ax_mr.add_patch(plt.Rectangle(cell, 1, 1, color='red', alpha=0.375, label='Main Route'))
    else:
        ax_mr.add_patch(plt.Rectangle(cell, 1, 1, color='red', alpha=0.375))

# Region -- Figure configurations
for ax in [ax_dc, ax_mr]:
    ax.set_xticks(np.arange(0, 100, 1))
    ax.set_yticks(np.arange(0, 100, 1))
    ax.grid()
    ax.set_axisbelow(True)
    ax.set_aspect('equal')
    ax.set_xlim(2, 10)
    ax.set_ylim(2, 10)
    ax.tick_params(left=False, right=False, labelleft=False,
                   labelbottom=False, bottom=False)
    ax.legend()

plt.show()
