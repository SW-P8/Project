from _typeshed import NoneType
import argparse
from DTC import dtc_executor, gridsystem, trajectory
from database.save_data import save_data
from database.db import init_db

class CleanTraj:

    def __init__(self) -> None:
        pass
    # Evt kør på en tråd for sig selv konstant
    def clean(self, points, safe_areas):
        traj = trajectory.Trajectory()
        traj.cls_input_list(points)
        traj_points = trajectory.TrajectoryPointCloud()
        traj_points.add_trajectory(traj)
        grid = gridsystem.GridSystem(points)
        noisy_points = self.update_safe_areas(grid, safe_areas) 
        self.add_noisy_points_to_noise_set(noisy_points) # - noisy_points should hold coordinates of closest safe_area 


    # this might not be smart
    def update_safe_areas(self, traj, safe_areas):
        pass
        #noise = call_lasses_insert_function(traj, safe_areas) #- this should maybe return points outside SA before cleaning them 
        #recalculate_safe_aread(noise, safe_areas) # magic function arthur cook


    # noise set save in DB?
    # load when supposed to be used?
    def add_noisy_points_to_noise_set(self, noisy_points):
        conn = init_db()
        save_data(None, conn, noisy_point=True, points=noisy_points)

        # could ret

    # argparse for input - listen for input
    # spin up a thread cleaning traj
    # lock gs with mutex when R/W operations are performed
    # argparse should take safe_areas and points as input
    def clean_loop(self, *args, **kwargs):
        sigterm = False
        while(not sigterm):
            if 'sigterm' in kwargs:
                sigterm = True
            if 'trajectory' in kwargs and 'safe_areas' in kwargs:
                self.clean(kwargs['trajectory'], kwargs['safe_areas'])
            else:
                return "either trajectory or safe_areas are wrong"


    

