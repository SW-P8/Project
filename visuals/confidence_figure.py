import matplotlib.pyplot as plt
import numpy as np

confidence = np.array([0.75, 0.7, 0.75, 0.7, 0.65])
time = np.array([0, 1, 1, 2, 2])
# Threshold line
threshold = 0.68

fig, ax = plt.subplots()

ax.plot(time, confidence, label='Confidence')

ax.axhline(y=threshold, color='r', linestyle='--', label='Threshold')

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_ylim(0.5, 1)
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Confidence', fontsize=12)
ax.set_xticks([])
ax.set_yticks([])

ax.set_title('Confidence Decay with Threshold and Events')

ax.legend(fontsize=12)

ax.annotate('Decay', xy=(0.3, 0.73), xytext=(0.2, 0.85),
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            fontsize=12)
ax.annotate('Point inserted inside safe area', xy=(1, 0.76), xytext=(0.6, 0.85),
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            fontsize=12)
ax.annotate('Point inserted outside safe area', xy=(2, 0.7), xytext=(1.2, 0.8),
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            fontsize=12)
plt.savefig("deeznuts.png")
