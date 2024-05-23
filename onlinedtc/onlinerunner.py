from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.noise_correction import NoiseCorrection
from collections import defaultdict
from datetime import datetime, timedelta
from progress.bar import Bar

import config


class RunCleaning():
    def __init__(self, safe_areas: dict, initialization_point: tuple, smoothed_main_route: defaultdict[set]) -> None:
        self.safe_areas = safe_areas
        self.initialization_point = initialization_point
        self.smooth_main_route = smoothed_main_route
        self.input_trajectories = []
        self.rebuild = True
        self.cleaner = None
        self.last_check = next(iter(safe_areas.values())).timestamp
        self.current_time = None

    def read_trajectories(self, point_cloud: TrajectoryPointCloud):
        for trajectory in point_cloud.trajectories:
            self.input_trajectories.append(trajectory)

    def clean_and_increment(self):
        bar = Bar('Incrementing... ', max=len(self.input_trajectories), suffix=' %(index)d/%(max)d - %(percent).1f%% - avg %(avg).1fs - elapsed %(elapsed)ds - ETA %(eta)ds')
        while self.input_trajectories:
            if self.rebuild:
                self.cleaner = NoiseCorrection(
                    self.safe_areas,
                    self.initialization_point,
                    self.smooth_main_route
                    )
                self.rebuild = True
            trajectory = self.input_trajectories.pop(0)
            self.current_time = trajectory.points[len(trajectory.points) - 1].timestamp
            self.cleaner.noise_detection(trajectory, self._rebuild_listener)
            self._check_time_call_update(self.current_time)
            bar.next()
        bar.finish()

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
        for safe_area in self.safe_areas.values():
            confidence, _ = safe_area.get_current_confidence(time_for_check)
            if confidence > config.confidence_threshold:
                new_safe_areas[safe_area.anchor] = safe_area
        self.safe_areas = new_safe_areas
        self.rebuild = True

    def _update_time(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0):
        self.current_time + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def _check_time_call_update(self, time: datetime):
        update_time = 24 * 3600 # System updates confidence of all safe-areas every 12 hours, timedelta uses seconds for unit.
        unused_safe_areas = []
        if (time - self.last_check).total_seconds() > update_time:
            for safe_area in self.safe_areas.values():
                safe_area.get_current_confidence(time)
                if safe_area.confidence < config.confidence_threshold:
                    unused_safe_areas.append(safe_area.anchor)
            for anchor in unused_safe_areas:
                self.safe_areas.pop(anchor)
            self.last_check = time
