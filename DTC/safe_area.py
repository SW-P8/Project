from operator import itemgetter
from datetime import datetime

class SafeArea:
    def __init__(self, anchor_cover_set, anchor: tuple[float, float], decrease_factor) -> None:
        self.center = anchor
        self.radius = 0
        self.weigth = 0
        self.timestamp = datetime.now() # Could be used to indicate creation or update time if we use time for weights, change value.
        self.construct(anchor_cover_set, decrease_factor)

    def construct(self, anchor, decrease_factor):
        self.calculate_radius(anchor, decrease_factor)
        self.calculate_weight()
       
    def calculate_radius(self, anchor, decrease_factor: float = 0.01):
        radius = max(anchor, key=itemgetter(1), default=(0,0))[1]
        removed_count = 0
        cover_set_size = len(anchor)
        removal_threshold = decrease_factor * cover_set_size
        filtered_cover_set = {(p, d) for (p, d) in anchor}

        #Refine radius of safe area radius
        while removed_count < removal_threshold:
            radius *= (1 - decrease_factor)
            filtered_cover_set = {(p, d) for (p, d) in filtered_cover_set if d <= radius}
            removed_count = cover_set_size - len(filtered_cover_set)

        self.radius = radius

    # TODO add logic for deciding weights.
    def calculate_weight(self):
        self.weigth = 1

