import argparse
from DTC import dtc_executor, gridsystem
from database import *


class CleanTraj:

    def __init__(self) -> None:
        pass
    # Evt kør på en tråd for sig selv konstant
    def clean(self, points, safe_areas):
        grid = gridsystem.GridSystem(points)
        traj = self.transfer_incoming_points_to_grid(grid)
        noisy_points = self.update_safe_areas(traj, safe_areas) 
        self.add_noisy_points_to_noise_set(noisy_points) # - noisy_points should hold coordinates of closest safe_area 


    # add kwargs to create_grid_system, create grid_system needs to be moved out
    # of grid_system, this goes for all "helper" methods
    def transfer_incoming_points_to_grid(self, grid):
        traj = self.extract_trajectories(grid)
        return traj

    def extract_trajectories(self, grid):
        pass

    # this might not be smart
    def update_safe_areas(self, traj, safe_areas):
        pass
        #noise = call_lasses_insert_function(traj, safe_areas) #- this should maybe return points outside SA before cleaning them 
        #recalculate_safe_aread(noise, safe_areas) # magic function arthur cook


    # noise set save in DB?
    # load when supposed to be used?
    def add_noisy_points_to_noise_set(self, noisy_points):
        create_sql_rel_to_nearest_sa(noisy_points) # sq'uee'l call 
        # could ret

    # argparse for input - listen for input
    # spin up a thread cleaning traj
    # lock gs with mutex when R/W operations are performed
    # argparse should take safe_areas and points as input
    def clean_loop(*args, **kwargs):
        sigterm = False
        while(not sigterm):
            if 'sigterm' in kwargs:
                sigterm = True
            if 'trajectory' in kwargs and 'safe_areas' in kwargs:
                self.clean(kwargs['trajectory'], kwargs['safe_areas'])
            else:
                return "either trajectory or safe_areas are wrong"


    

