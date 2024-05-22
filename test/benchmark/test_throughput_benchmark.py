import pytest
from DTC.noise_correction import NoiseCorrection
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.distance_calculator import DistanceCalculator
from DTC.route_skeleton import RouteSkeleton
from onlinedtc.increment import update_safe_area
from copy import deepcopy
import config

class TestThroughputBenchmark:
    @pytest.fixture
    def trajectory(self):
        trajectory = Trajectory()
        for i in range(1000):
            trajectory.add_point(i * 0.00001, 0.0001, None)
        return trajectory
    
    @pytest.fixture
    def grid_system(self, trajectory):
        point_cloud = TrajectoryPointCloud()
        point_cloud.add_trajectory(trajectory)
        grid_system = GridSystem(point_cloud)
        grid_system.create_grid_system()
        grid_system.extract_main_route()
        grid_system.extract_route_skeleton()
        grid_system.construct_safe_areas(0)
        return grid_system

    @pytest.mark.bm_throughput
    def test_cleaning_throughput(self, benchmark, trajectory, grid_system):
        noise_corrector = NoiseCorrection(grid_system.safe_areas, grid_system.initialization_point, with_iteration=False)

        # Make every second point noisy
        for i in range(0, 1000, 2):
            trajectory.points[i].latitude = DistanceCalculator.shift_point_with_bearing(trajectory.points[i], 105, config.SOUTH)[1]
        
        # Calculate the total number of deepcopies needed
        rounds = 5
        iterations = 3
        warmup_rounds = 2
        total_iterations = (rounds + warmup_rounds) * iterations + 1

        # Pre-create deepcopies of trajectory
        list_of_lists_of_trajectories = [[deepcopy(trajectory) for _ in range(10)] for _ in range(total_iterations)]

        # Index to track the current deepcopy to use
        index = [0]

        # We use wrapper which calls its own deepcopy of the trajectories to avoid each iteration impacting the next
        def noise_detection_wrapper():
            current_list_of_trajectories = list_of_lists_of_trajectories[index[0]]
            for current_trajectory in current_list_of_trajectories:
                noise_corrector.noise_detection(trajectory=current_trajectory)
            index[0] += 1

        benchmark.pedantic(noise_detection_wrapper, rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds)

    @pytest.mark.bm_throughput
    def test_iterating_throughput(self, benchmark, trajectory,grid_system):
        old_smoothed_main_route = RouteSkeleton.smooth_main_route(grid_system.main_route)
        noise_corrector = NoiseCorrection(grid_system.safe_areas, grid_system.initialization_point)

        # Make every second point noisy
        for i in range(1000):
            trajectory.points[i].latitude = DistanceCalculator.shift_point_with_bearing(trajectory.points[i], 105, config.SOUTH)[1]

        noise_corrector.noise_detection(trajectory)

        # Calculate the total number of deepcopies needed
        rounds = 5
        iterations = 3
        warmup_rounds = 2
        total_iterations = (rounds + warmup_rounds) * iterations + 1

        # Pre-create deepcopies of trajectory
        list_of_lists_of_safe_areas_and_smr = [[(deepcopy(grid_system.safe_areas), deepcopy(old_smoothed_main_route)) for _ in range(10)] for _ in range(total_iterations)]
    
        # Index to track the current deepcopy to use
        index = [0]

        def update_safe_area_wrapper():
            current_list_of_safe_areas_and_smr = list_of_lists_of_safe_areas_and_smr[index[0]]
            for current_safe_areas, current_smr in current_list_of_safe_areas_and_smr:
                update_safe_area(current_safe_areas, grid_system.initialization_point, current_smr)
            index[0] += 1

        benchmark.pedantic(update_safe_area_wrapper, rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds)