import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

points = [
    (1,1),
    (1,2),
    (1,3),
    (2,1),
    (2,2),
    (2,3),
    (3,1),
    (3,2),
    (3,3),
]

fig, ax = plt.subplots()
grid_ticks = np.arange(0, 100, 1)
ax.set_xticks(grid_ticks)
ax.set_yticks(grid_ticks)
ax.grid()

for point in points:
    x,y = point
    ax.scatter(x, y, color='g')
plt.show()