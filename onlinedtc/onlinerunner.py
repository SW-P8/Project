from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.noise_correction import NoiseCorrection
from collections import defaultdict
from datetime import datetime, timedelta

import json


class RunCleaning():
    def __init__(self, grid_system: GridSystem, smoothed_main_route: defaultdict[set]) -> None:
        self.grid_system = grid_system
        for attr_name in dir(grid_system):
            attr = getattr(grid_system, attr_name)
            if attr is None:
                raise AttributeError(f"Attribute: {attr_name} in grid system was None. All fields in grid system need to be filled for cleaning.")
        self.input_trajectories = []
        self.rebuild = True
        self.cleaner = None
        self.smooth_main_route = smoothed_main_route
        self.current_time = datetime.now()

    def read_trajectories(self, point_cloud: TrajectoryPointCloud):
        for trajectory in point_cloud.trajectories:
            self.input_trajectories.append(trajectory)

    def clean_and_increment(self):
        while self.input_trajectories:
            self.current_time = datetime.now()
            if self.rebuild:
                self.cleaner = NoiseCorrection(
                    self.grid_system.safe_areas,
                    self.grid_system.initialization_point,
                    self.smooth_main_route
                    )
                self.rebuild = False
            trajectory = self.input_trajectories.pop(0)
            self.cleaner.noise_detection(trajectory, self._rebuild_listener)
            self._append_to_json(trajectory)

    def _append_to_json(self, trajectory: Trajectory):
        if trajectory is None:
            raise AttributeError("Trajectory is none after cleaning")

        with open("cleaned_trajectories.json", "a") as json_file:
            json.dump(trajectory, json_file)
            json_file.write("\n")

    def _rebuild_listener(self):
        self.read_trajectories = True

    def _confidence_check_safe_areas(self, time_for_check: datetime):
        for safe_area in self.grid_system.safe_areas:
            safe_area.get_current_confidence(time_for_check)
        self.rebuild = True

    def _update_time(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0):
        self.current_time + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
