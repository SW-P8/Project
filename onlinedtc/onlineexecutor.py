from onlinedtc.increment import update_safe_area
from DTC.noise_correction import NoiseCorrection
from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory

class Application():
    def __init__(self, grid_system: GridSystem) -> None:
        self.grid_system = grid_system
        self.input_trajectories = list()
        self.rebuild = False
    
    def clean_and_increment(self, data: list[Trajectory], smoothed_main_route):
        self.cleaner = NoiseCorrection(self.grid_system.safe_areas, self.grid_system.initialization_point, smoothed_main_route)

        while data:
            if self.rebuild:
                self.cleaner = NoiseCorrection(self.grid_system.safe_areas, self.grid_system.initialization_point, smoothed_main_route)
                self.rebuild = False
            trajectory = data.pop(0)
            self.cleaner.noise_detection(trajectory, self._rebuild_kdtree)
        

    def insert_data(data: list[Trajectory]):
        pass

    def _rebuild_kdtree(self):
        self.rebuild = True