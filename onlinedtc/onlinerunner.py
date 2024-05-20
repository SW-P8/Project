from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.noise_correction import NoiseCorrection
from collections import defaultdict
from datetime import datetime, timedelta

import json
import config


class RunCleaning():
    def __init__(self, grid_system: GridSystem, smoothed_main_route: defaultdict[set]) -> None:
        self.grid_system = grid_system
        for attr_name, value in vars(grid_system).items():
            if attr_name not in attr_names:
                continue
            if value is None or (isinstance(value, (dict, list, set, tuple, str)) and len(value) == 0):
                raise AttributeError(f"Attribute: {attr_name} in grid system was None. All fields in grid system need to be filled for cleaning.")
        self.input_trajectories = []
        self.rebuild = True
        self.cleaner = None
        self.smooth_main_route = smoothed_main_route
        self.last_check = datetime.now()
        self.current_time = None

    def read_trajectories(self, point_cloud: TrajectoryPointCloud):
        for trajectory in point_cloud.trajectories:
            self.input_trajectories.append(trajectory)

    def clean_and_increment(self):
        while self.input_trajectories:
            if self.rebuild:
                #print(f"building cleaner with safe areas {self.grid_system.safe_areas}")
                self.cleaner = NoiseCorrection(
                    self.grid_system.safe_areas,
                    self.grid_system.initialization_point,
                    self.smooth_main_route
                    )
                self.rebuild = True
            trajectory = self.input_trajectories.pop(0)
            print(trajectory.points)
            self.current_time = trajectory.points[len(trajectory.points) - 1].timestamp
            self.cleaner.noise_detection(trajectory, self._rebuild_listener)
            self._check_time_call_update(self.current_time)
            self._append_to_json(trajectory)

    def _append_to_json(self, trajectory: Trajectory):
        if trajectory.points == []:
            return

        with open("cleaned_trajectories.json", "a") as json_file:
            json_file.write(trajectory.to_json())
            json_file.write('\n')

    def _rebuild_listener(self):
        self.read_trajectories = True

    def _confidence_check_safe_areas(self, time_for_check: datetime):
        new_safe_areas = {}
        for safe_area in self.grid_system.safe_areas.values():
            confidence, _ = safe_area.get_current_confidence(time_for_check)
            print("checking a thing")
            if confidence > 0.5:
                new_safe_areas[safe_area.anchor] = safe_area
        self.grid_system.safe_areas = new_safe_areas
        self.rebuild = True

    def _update_time(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0):
        self.current_time + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def _check_time_call_update(self, time: datetime):
        update_time = 24 * 3600 # System updates confidence of all safe-areas every 12 hours, timedelta uses seconds for unit.
        unused_safe_areas = []
        if (time - self.last_check).total_seconds() > update_time:
            for safe_area in self.grid_system.safe_areas.values():
                safe_area.get_current_confidence(time)
                print(
                    f"triggered, checking safe area: {safe_area.anchor}, time difference = {(time - self.last_check)}")
                if safe_area.confidence < config.confidence_threshold:
                    unused_safe_areas.append(safe_area.anchor)
            for anchor in unused_safe_areas:
                print(f"popping safe area {anchor} which held {len(self.grid_system.safe_areas[anchor].points_in_safe_area.points)} points, with radius {self.grid_system.safe_areas[anchor].radius}, and had timestamp {self.grid_system.safe_areas[anchor].timestamp}, and confidence {self.grid_system.safe_areas[anchor].confidence}")
                self.grid_system.safe_areas.pop(anchor)
            self.last_check = time


attr_names = ['pc', 'initialization_point', 'grid', 'main_route', 'route_skeleton', 'safe_areas']
