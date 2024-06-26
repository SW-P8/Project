# Direction constants
NORTH = 0
EAST = 90
SOUTH = 180
WEST = 270

# Metric constants
CELL_SIZE = 5         # Based on observation in DTC paper that minimal width of a road is 5m
NEIGHBORHOOD_SIZE = 9 # To be determined but DTC uses 9


# Safe Area
decrease_factor = 0.1
max_radius = 20
decay_factor = 1 / (60*60*24)
confidence_change = 0.01
cardinality_squish = 0.01
max_confidence_change = 0.1
linear_decay = 1 / 86400

# Confidence increase and decrease
confidence_increase = 0.025
confidence_decrease_scale_factor = 1
max_confidence_decrease = 0.025
confidence_threshold = 0.5

# Route Skeleton
smooth_radius = 20
'''Cell neighborhood for smoothing.'''
filtering_list_radius = 15
'''Epsilon for DB-Scan.'''
min_pts_from_mr = 0.0001
'''What percentage of the size of the main route should a component have.'''
distance_interval = 15  # Distance for sampling.
'''Distance for sampling a graphed smoothed main route.'''

# Main Route
distance_scale = 0.2
'''Multiplier for distance away from neighborhood in main route extraction.'''


# Incremental
update_time = 24 * 3600 # System updates confidence of all safe-areas every 12 hours, timedelta uses seconds for unit.

