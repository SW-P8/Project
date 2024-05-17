# Direction constants
NORTH = 0
EAST = 90
SOUTH = 180
WEST = 270

# Metric constants
CELL_SIZE = 5         # Based on observation in DTC paper that minimal width of a road is 5m
NEIGHBORHOOD_SIZE = 9 # To be determined but DTC uses 9


# Safe Area
decrease_factor = 0.01
decay_factor = 1 / (60*60*24)
confidence_change = 0.01
cardinality_squish = 0.01
max_confidence_change = 0.1
linear_decay = 1 / 200000

# Route Skeleton
smooth_radius = 25
filtering_list_radius = 20
distance_interval = 20
distance_scale = 0.2