import numpy as np
import matplotlib.pyplot as plt

from DTC.construct_main_route import ConstructMainRoute
from DTC.distance_calculator import DistanceCalculator
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea

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

main_route = ConstructMainRoute.extract_main_route_with_density_center(grid_system)
route_skeleton = RouteSkeleton.extract_route_skeleton(ConstructMainRoute.extract_main_route(grid_system),1, 1, 1)
candidates, historic_mindist = ConstructSafeArea.find_candidate_nearest_neighbors_with_historic_mindist(route_skeleton, (5, 5))
# Region -- Insert data into figures
fig_dc, ax_dc = plt.subplots()
fig_mr, ax_mr = plt.subplots()
fig_cnn, ax_cnn = plt.subplots()

# Density center figure
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

# Main route figure
first_active = True
first_inactive = True
for cell, density_center, active in main_route:
    x_c, y_c = cell
    x_d, y_d = density_center
    color = 'green' if active else 'red'
    label = ('Main Route' if first_active and active else
            ('Not included in main route' if first_inactive and not active else None))
    
    ax_mr.add_patch(plt.Rectangle(cell, 1, 1, color=color, alpha=0.375, label=label))
    ax_mr.scatter(x_d, y_d, color=color)
    ax_mr.plot([x_c, x_d], [y_c, y_d], color=color, zorder=0)
    
    if first_active and active:
        first_active = False
    if first_inactive and not active:
        first_inactive = False

# Candidate Nearest Neighbor Figure
ax_cnn.add_patch(plt.Rectangle((5, 5), 1, 1, color='green', alpha=0.375, label='cell'))
for anchor in route_skeleton:
    x_a, y_a = anchor
    ax_cnn.scatter(*anchor, color='orange')
    ax_cnn.plot([x_a, 5], [y_a, 5], color='orange', zorder=0)
for candidate in candidates:
    ax_cnn.scatter(*candidate, color='green')
for dist in historic_mindist:
    ax_cnn.add_patch(plt.Circle((5.5, 5.5), dist, color ='green', fill=False))

# Region -- Figure configurations
for ax in [ax_dc, ax_mr, ax_cnn]:
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
