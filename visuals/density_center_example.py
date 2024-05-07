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
candidae_points = [
    (3.1, 3.3, 'red'),
    (3.8, 3.8, 'red'),
    (4.5, 4.2, 'red'),
    (4.5, 4.8, 'red'),
    (5.1, 5.1, 'green'),
    (5.1, 5.3, 'green'),
    (5.3, 5.1, 'green'),
    (5.3, 5.3, 'green'),
    (4.7, 5.1, 'green'),
    (4.7, 5.2, 'green'),
    (6.8, 5.1, 'red'),
    (6.8, 5.2, 'red'),
    (7.2, 4.4, 'red'),
    (7.2, 4.8, 'red'),
    (7.6, 4.4, 'red'),
    (8.8, 3.2, 'red')
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
route_skeleton = RouteSkeleton.extract_route_skeleton(ConstructMainRoute.extract_main_route(grid_system),1, 1, 1)
candidates, historic_mindist = ConstructSafeArea.find_candidate_nearest_neighbors_with_historic_mindist(route_skeleton, (5, 5))
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
    label = ('Main Route' if first_active and active else
            ('Not included in main route' if first_inactive and not active else None))
    
    ax_cmr.add_patch(plt.Rectangle(cell, 1, 1, color=color, alpha=0.375, label=label))
    ax_cmr.plot([x_c, x_d], [y_c, y_d], linestyle='--', dashes=(2, 1), linewidth=1, color=color)

    if first_active and active:
        first_active = False
    if first_inactive and not active:
        first_inactive = False

ax_cmr.scatter(*zip(*points), color='g', label='Point')
ax_cmr.scatter(*zip(*density_centers.values()), color='orange',
               marker='D', label='Density center')
ax_cmr.add_patch(plt.Rectangle((2.02, 2.02), 2.98, 2.98, linestyle='--', fill=False, color='green', linewidth=2))
ax_cmr.text(3.65, 3.40, r'$\Omega_{1,1}=(1.5, 1.5)$')
# Candidate Nearest Neighbor Figure
for point in candidae_points:
    x, y, color = point
    ax_cnn.scatter(x, y, color=color)
ax_cnn.scatter(5.5, 5.5, color='green')
ax_cnn.add_patch(plt.Circle((5.5, 5.5), 0.7, color ='green', fill=False))
ax_cnn.add_patch(plt.Circle((5.5, 5.5), 1, color ='green', fill=False, linestyle='--'))

ax_cnn.plot([5.5, 5.5], [5.5, 4.8], linestyle='--', dashes=(2, 1), linewidth=1, color='green')
ax_cnn.text(5.6, 5.2, 'mindist', fontsize=10)

ax_cnn.plot([5.5, 5.5], [4.8, 4.5], linestyle='--', dashes=(2, 1), linewidth=1, color='green')
ax_cnn.text(5.6, 4.6, u'\u03B5', fontsize=10)

# Region -- Figure configurations
for ax in [ax_cmr, ax_cnn]:
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
