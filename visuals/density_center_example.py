import numpy as np
import matplotlib.pyplot as plt

from DTC.construct_main_route import ConstructMainRoute
from DTC.distance_calculator import DistanceCalculator
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea

# Region -- Arrange Data
points = [
    (3.1, 3.3),
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
psi_points = [
    (5.1, 5.1),
    (5.7, 5.6),
    (5.5, 5.8),
    (5.9, 5.9),
]

anchors = [
    (2.2, 3.1),
    (3.5, 4),
    (6, 6),
    (7, 7.5),
    (4.5, 4.5),
    (6, 3.2),
    (7.3, 2.5)
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

main_route = ConstructMainRoute.extract_main_route_with_density_center(grid_system)
route_skeleton = RouteSkeleton.extract_route_skeleton(ConstructMainRoute.extract_main_route(grid_system), 2, 50, 0)
# Region -- Insert data into figures
fig_cmr, ax_cmr = plt.subplots()
fig_cnn, ax_cnn = plt.subplots()

# Construct Main route figure
first_active = True
first_inactive = True
for cell, density_center, active in main_route:
    x_c, y_c = cell
    x_d, y_d = density_center
    color = 'green' if active else 'red'
    label = ('Main route' if first_active and active else
            ('Not included in main route' if first_inactive and not active else None))
    
    ax_cmr.add_patch(plt.Rectangle(cell, 1, 1, color=color, alpha=0.375, label=label))
    ax_cmr.plot([x_c, x_d], [y_c, y_d], linestyle='--', dashes=(2, 1), linewidth=1, color=color)
    #ax_cnn.add_patch(plt.Rectangle(cell, 1, 1, color=color, alpha=0.375, label=label))
    if first_active and active:
        first_active = False
    if first_inactive and not active:
        first_inactive = False

ax_cmr.scatter(*zip(*points), color='b', label='Point')
ax_cmr.scatter(*zip(*density_centers.values()), color='Black',
               marker='D', label='Density centre')
ax_cmr.add_patch(plt.Rectangle((2.02, 2.02), 2.98, 2.98, linestyle='--', fill=False, color='green', linewidth=2))
ax_cmr.text(3.65, 3.40, r'$\Omega_{1,1}=(1.5, 1.5)$')
# Safe Area Construction Figure
min_dist = float('inf')
for anchor in anchors:
    dist = DistanceCalculator.calculate_euclidian_distance_between_cells((5.5, 5.5), anchor)
    if dist < min_dist:
        min_dist = dist
ax_cnn.add_patch(plt.Circle((5.5, 5.5), min_dist + np.sqrt(2), alpha=0.2, color='r'))
ax_cnn.add_patch(plt.Circle((5.5, 5.5), min_dist, alpha=0.5, color='g'))
ax_cnn.scatter(*zip(*psi_points), color='b', label='Point')
ax_cnn.scatter(*zip(*anchors), color='black', marker='D', label='Anchor')

# Region -- Figure configurations
i = 0
for ax in [ax_cmr, ax_cnn]:
    i += 1
    ax.set_xticks(np.arange(0, 100, 1))
    ax.set_yticks(np.arange(0, 100, 1))
    ax.grid()
    ax.set_axisbelow(True)
    ax.set_aspect('equal')
    ax.set_xlim(2, 9)
    ax.set_ylim(2, 9)
    ax.tick_params(left=False, right=False, labelleft=False,
                   labelbottom=False, bottom=False)
    ax.legend()

fig_cmr.savefig("figure1.png")
fig_cnn.savefig("figure2.png")
