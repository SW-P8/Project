import matplotlib.pyplot as plt
import numpy as np

confidence = np.array([0.75, 0.7, 0.75, 0.7, 0.6])
time = np.array([0, 1, 1, 2, 2])
# Threshold line
threshold = 0.62    

fig, ax = plt.subplots()

ax.plot(time, confidence, label='Confidence')

ax.axhline(y=threshold, color='r', linestyle='--', label='Threshold')

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_ylim(0.5, 1)
ax.set_xlabel('Time')
ax.set_ylabel('Confidence')
ax.set_xticks([])
ax.set_yticks([])

ax.set_title('Confidence Decay with Threshold and Events')

ax.legend()

ax.annotate('Decay', xy=(0.5, 0.73), xytext=(0.4, 0.85),
            arrowprops=dict(facecolor='black', arrowstyle='->'))
ax.annotate('Increase', xy=(1, 0.76), xytext=(0.87, 0.85),
            arrowprops=dict(facecolor='black', arrowstyle='->'))
ax.annotate('Decrease', xy=(2, 0.7), xytext=(1.85, 0.85),
            arrowprops=dict(facecolor='black', arrowstyle='->'))
plt.show()
