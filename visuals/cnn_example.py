import matplotlib.pyplot as plt
import numpy as np

# Function to plot circles
def plot_circle(ax, center, radius, color='b', alpha=0.2):
    circle = plt.Circle(center, radius, color=color, alpha=alpha)
    ax.add_patch(circle)

# Function to plot points
def plot_points(ax, points, color='r'):
    ax.scatter(points[:, 0], points[:, 1], color=color)

# Generate random points for demonstration
np.random.seed(0)
num_points = 100
points = np.random.rand(num_points, 2) * 10  # Random points in a 10x10 space

# Random anchor points
anchors = np.array([[2, 3], [6, 7], [8, 2]])

# Plotting
fig, ax = plt.subplots(figsize=(8, 8))

# Plot all points
plot_points(ax, points)

# Plot anchor points
plot_points(ax, anchors, color='b')

# Plot circles representing safe areas
for anchor in anchors:
    center = anchor
    
    # Plot inner circle (mindist)
    inner_radius = np.sqrt(0.5 ** 2 + 0.5 ** 2)  # padding distance
    plot_circle(ax, center, inner_radius, color='g', alpha=0.2)

    # Plot outer circle (mindist + epsilon)
    outer_radius = np.sqrt(0.5 ** 2 + 0.5 ** 2) * 2  # mindist + epsilon
    plot_circle(ax, center, outer_radius, color='y', alpha=0.2)

# Plotting details
ax.set_aspect('equal', 'box')
ax.set_title('Safe Area Construction')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_xticks(np.arange(0, 11, step=1))
ax.set_yticks(np.arange(0, 11, step=1))
ax.grid(True)
plt.show()
