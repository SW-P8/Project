from DTC.distance_calculator import DistanceCalculator

class ConstructMainRoute:
    @staticmethod
    def extract_main_route(grid: dict, distance_scale: float = 0.2) -> set:
        main_route = set()

        if distance_scale >= 0.5:
            raise ValueError("distance scale must be less than neighborhood size divided by 2")
        
        distance_threshold = distance_scale * DistanceCalculator.NEIGHBORHOOD_SIZE

        for cell in grid.keys():
            density_center = ConstructMainRoute.calculate_density_center(cell, grid)
            if DistanceCalculator.calculate_euclidian_distance_between_cells(cell, density_center) < distance_threshold:
                main_route.add(cell)
        
        return main_route

    @staticmethod
    def extract_main_route_with_density_center(grid: dict, distance_scale: float = 0.2):
        """This method is used for visualisation"""
        main_route = set()

        if distance_scale >= 0.5:
            raise ValueError("distance scale must be less than neighborhood size divided by 2")
        
        distance_threshold = distance_scale * DistanceCalculator.NEIGHBORHOOD_SIZE

        for cell in grid.keys():
            density_center = ConstructMainRoute.calculate_density_center(cell, grid)
            if DistanceCalculator.calculate_euclidian_distance_between_cells(cell, density_center) < distance_threshold:
                main_route.add((cell, density_center, True))
            else:
                main_route.add((cell, density_center, False))
        
        return main_route

    @staticmethod
    def calculate_density_center(index, grid: dict) -> tuple[float, float]:
        (x, y) = index
        l = DistanceCalculator.NEIGHBORHOOD_SIZE // 2
        point_count = 0
        (x_sum, y_sum) = (0, 0)
 
        for i in range(x - l, x + l + 1):
            for j in range(y - l, y + l + 1):
                if (i, j) in grid.keys():
                    cardinality = len(grid[(i, j)])
                    x_sum += cardinality * i
                    y_sum += cardinality * j
                    point_count += cardinality

        if x_sum != 0:
            x_sum /= point_count

        if y_sum != 0:
            y_sum /= point_count

        return (x_sum, y_sum)
