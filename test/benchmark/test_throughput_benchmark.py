import pytest
from DTC.noise_correction import NoiseCorrection
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.distance_calculator import DistanceCalculator
from DTC.route_skeleton import RouteSkeleton
from DTC.dtc_executor import DTCExecutor
from onlinedtc.increment import update_safe_area
from copy import deepcopy
from math import ceil
import random
import config

class TestThroughputBenchmark:
    @pytest.fixture
    def point_clouds(self):
        dtc_executor = DTCExecutor(False)
        full_point_cloud = dtc_executor.create_point_cloud_with_n_points(2000000)
        first_half_trajectories = full_point_cloud.trajectories[:len(full_point_cloud.trajectories)//2]
        first_half_point_cloud = TrajectoryPointCloud()
        for trajectory in first_half_trajectories:
            first_half_point_cloud.add_trajectory(trajectory)
        second_half_trajectories = full_point_cloud.trajectories[len(full_point_cloud.trajectories)//2:]
        second_half_point_cloud = TrajectoryPointCloud()
        for trajectory in second_half_trajectories:
            second_half_point_cloud.add_trajectory(trajectory)
        return first_half_point_cloud, second_half_point_cloud

    
    @pytest.fixture
    def grid_system(self, point_clouds):    
        grid_system = GridSystem(point_clouds[0])
        grid_system.create_grid_system()
        grid_system.extract_main_route()
        grid_system.extract_route_skeleton()
        grid_system.construct_safe_areas(0.01)
        return grid_system

    @pytest.mark.bm_throughput
    def test_cleaning_throughput(self, benchmark, point_clouds, grid_system):
        noise_corrector = NoiseCorrection(grid_system.safe_areas, grid_system.initialization_point, with_iteration=False)
        all_points = []
        
        #clean trajectories in second half and then make every second point noisy
        for trajectory in point_clouds[1].trajectories:
            noise_corrector.noise_detection(trajectory)
            all_points.extend(trajectory.points)

        amount_to_shift = ceil(len(all_points) * 0.05)
        points_to_shift = random.sample(all_points, amount_to_shift)

        for point in points_to_shift:
            point.set_coordinates(DistanceCalculator.shift_point_with_bearing(point, random.randint(1,200), random.randint(0,359)))

        # Calculate the total number of deepcopies needed
        rounds = 1
        iterations = 1
        warmup_rounds = 0
        total_iterations = (rounds + warmup_rounds) * iterations #+ 1

        # Pre-create deepcopies of trajectory
        list_of_noisy_point_clouds = [deepcopy(point_clouds[1]) for _ in range(total_iterations)]

        # Index to track the current deepcopy to use
        index = [0]

        # We use wrapper which calls its own deepcopy of the noisy point cloud to avoid each iteration impacting the next
        def noise_detection_wrapper():
            print("Total point count: ", len(all_points))
            print("Points shifted: ", amount_to_shift)
            current_noisy_point_cloud = list_of_noisy_point_clouds[index[0]]
            for current_trajectory in current_noisy_point_cloud.trajectories:
                noise_corrector.noise_detection(trajectory=current_trajectory)
            index[0] += 1

        benchmark.pedantic(noise_detection_wrapper, rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds)

#    @pytest.mark.bm_throughput
#    def test_iterating_throughput(self, benchmark, trajectory,grid_system):
#        old_smoothed_main_route = RouteSkeleton.smooth_main_route(grid_system.main_route)
#        noise_corrector = NoiseCorrection(grid_system.safe_areas, grid_system.initialization_point)
#
#        # Make every point noisy to ensure creation of 10 new safe areas
#        for i in range(1000):
#            trajectory.points[i].latitude = DistanceCalculator.shift_point_with_bearing(trajectory.points[i], 105, config.SOUTH)[1]
#
#        noise_corrector.noise_detection(trajectory)
#
#        # Calculate the total number of deepcopies needed
#        rounds = 5
#        iterations = 3
#        warmup_rounds = 2
#        total_iterations = (rounds + warmup_rounds) * iterations + 1
#
#        # Pre-create deepcopies of trajectory
#        list_of_lists_of_safe_areas_and_smr = [[(deepcopy(grid_system.safe_areas), deepcopy(old_smoothed_main_route)) for _ in range(20)] for _ in range(total_iterations)]
#    
#        # Index to track the current deepcopy to use
#        index = [0]
#
#        def update_safe_area_wrapper():
#            current_list_of_safe_areas_and_smr = list_of_lists_of_safe_areas_and_smr[index[0]]
#            for current_safe_areas, current_smr in current_list_of_safe_areas_and_smr:
#                update_safe_area(current_safe_areas, grid_system.initialization_point, current_smr)
#            index[0] += 1
#
#        benchmark.pedantic(update_safe_area_wrapper, rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds)