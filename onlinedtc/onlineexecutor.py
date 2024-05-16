from DTC.noise_correction import NoiseCorrection
from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory

import time
import threading
import os


class CleaningApplication():
    def __init__(self, grid_system: GridSystem) -> None:
        self.grid_system = grid_system
        self.input_trajectories = list()
        self.rebuild = False
        self.cleaner = None
        self.smoothed_main_route = None

    def start_cleaning(self, smoothed_main_route):
        self.smoothed_main_route = smoothed_main_route

        data_folder = 'input_data'
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        cleaning_thread = threading.Thread(target=self._continuous_cleaning)
        cleaning_thread.daemon = True
        cleaning_thread.start()

    def clean_and_increment(self, data: Trajectory, smoothed_main_route):
        if self.cleaner is None:
            self.cleaner = NoiseCorrection(
                self.grid_system.safe_areas,
                self.grid_system.initialization_point,
                smoothed_main_route)

        if self.rebuild:
            self.cleaner = NoiseCorrection(
                self.grid_system.safe_areas,
                self.grid_system.initialization_point,
                smoothed_main_route)
            self.rebuild = False

        self.cleaner.noise_detection(data, self._rebuild_kdtree)

    def insert_data(self, data: Trajectory):
        self.input_trajectories.extend(data)

    def add_time(self, hours: int = 1):
        pass  # TODO: implement this method.

    def _continuous_cleaning(self):
        while True:
            if self.input_trajectories:
                self.clean_and_increment(self.input_trajectories.pop[0],
                                         self.smoothed_main_route)
            else:
                time.sleep(1)

    def _rebuild_kdtree(self):
        self.rebuild = True
