import matplotlib.pyplot as plt
from DTC.json_read_write import read_safe_areas_from_json, write_safe_areas_to_json, read_point_cloud_from_json, write_point_cloud_to_json, read_set_of_tuples_from_json, write_set_of_tuples_to_json


smr = read_set_of_tuples_from_json("Results/safe_areas_before_incremental_0.025_1_0.025_0.4.json")

fig, ax = plt.subplots()
ax.scatter(*zip(*smr), color='g', s=0.01)



ax.set_ylim(0, 7000)
ax.set_xlim(0, 7000)
ax.set_aspect('equal', 'box')
ax.set_title("Skeleton with chosen parameters")
plt.savefig(f"Results/pngs/safe_areas_singular.png", dpi=900)

