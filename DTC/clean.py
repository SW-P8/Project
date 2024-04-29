from _typeshed import NoneType
import argparse
from DTC import dtc_executor, gridsystem, trajectory, noise_correction,distance_calculator
from database.save_data import save_data
from database.db import init_db
from DTC.distance_calculator import DistanceCalculator

class CleanTraj:

    def __init__(self, gridsystem : gridsystem.GridSystem) -> None:
        self.gridsystem = gridsystem


    def clean(self, points, safe_areas):
        traj = trajectory.Trajectory()
        traj.points = points
        distance_calc = distance_calculator.DistanceCalculator()
        for point in points:
            point = distance_calc.calculate_exact_index_for_point(point, self.gridsystem.initialization_point)
        noise_corrector = noise_correction.NoiseCorrection(self.gridsystem)
        points_sorted = noise_corrector.noise_detection(traj)
        
        noisy_points = [x for xs, _ in points_sorted for x in xs]
        clear_points = [y for _, ys in points_sorted for y in ys]

        noisy_points = self.update_safe_areas(noisy_points, self.gridsystem) 
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


    

