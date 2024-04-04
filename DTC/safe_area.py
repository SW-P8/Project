from operator import itemgetter

class SafeArea:
    def __init__(self, anchor) -> None:
        self.center = (0, 0)
        self.radius = 0
        self.weigth = 0 
        self.construct(anchor)

    def construct(self, anchor):
        #Initialize safe area radius
        self.calculate_radius(anchor)
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

