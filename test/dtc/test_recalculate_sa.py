#import pytest
import sys
import os

# Add the directory containing the DTC package to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
#from DTC.noise_correction import NoiseCorrection
from DTC.distance_calculator import DistanceCalculator
import copy
import config



class TestNoiseCorrection():    
    #@pytest.fixture
    def fifty_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()

        # Add initial point
        t.add_point(1, 1)

        for i in range(1, 51):
            # Shift points 40 meters east each time to create 50 points in a line along the x-axis
            shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 40, config.EAST)
            t.add_point(shifted_point[0], shifted_point[1])

        pc.add_trajectory(t)
        gs = GridSystem(pc) 
        gs.create_grid_system()
        return gs

   
e = TestNoiseCorrection()
gs = e.fifty_point_grid()

gs.construct_safe_areas()
print(gs.safe_areas)