import pytest
import pandas as pd

from DTC import trajectory

@pytest.mark.skip
@pytest.mark.bm_cheap
class benchmark_cheap():
    @pytest.fixture
    def small_points():
        

    def benchamrk_createTrajectory_100Points(benchmark):
        trj = trajectory.Trajectory()
        points = 
        benchmark.pedantic(add_points_to_trajectory, args=(trj, point), rounds=100, iterations=1)
    
    def add_points_to_trajectory(trajectory, points):
        for _, point in points:
            trajectory.add_point(point)