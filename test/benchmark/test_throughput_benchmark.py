import pytest
from DTC.noise_correction import NoiseCorrection
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.distance_calculator import DistanceCalculator
from DTC.route_skeleton import RouteSkeleton
from DTC.dtc_executor import DTCExecutor
from DTC.point import Point
from onlinedtc.increment import update_safe_area
from copy import deepcopy
from math import ceil
import random

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

        print("Total point count: ", len(all_points))
        print("Points shifted: ", amount_to_shift)

        for point in points_to_shift:
            point.set_coordinates(DistanceCalculator.shift_point_with_bearing(point, random.randint(1,200), random.randint(0,359)))

        # Calculate the total number of deepcopies needed
        rounds = 5
        iterations = 3
        warmup_rounds = 2
        total_iterations = (rounds + warmup_rounds) * iterations + 1

        # Pre-create deepcopies of trajectory
        list_of_noisy_point_clouds = [deepcopy(point_clouds[1]) for _ in range(total_iterations)]

        # Index to track the current deepcopy to use
        index = [0]

        # We use wrapper which calls its own deepcopy of the noisy point cloud to avoid each iteration impacting the next
        def noise_detection_wrapper():
            current_noisy_point_cloud = list_of_noisy_point_clouds[index[0]]
            for current_trajectory in current_noisy_point_cloud.trajectories:
                noise_corrector.noise_detection(trajectory=current_trajectory)
            index[0] += 1

        benchmark.pedantic(noise_detection_wrapper, rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds)

    @pytest.mark.bm_throughput
    def test_iterating_throughput(self, benchmark, block_point_cloud):
        points_in_sa_pc = 1000

        grid_system = GridSystem(block_point_cloud)
        grid_system.create_grid_system()
        grid_system.extract_main_route()
        old_smoothed_main_route = RouteSkeleton.smooth_main_route(grid_system.main_route)
        grid_system.extract_route_skeleton(distance_interval=10)
        grid_system.construct_safe_areas()
        print("Incrementing ",len(grid_system.route_skeleton), " safe areas with ", points_in_sa_pc, " points in each")

        for safe_area in grid_system.safe_areas.values():
            safe_area_point = DistanceCalculator.convert_cell_to_point(grid_system.initialization_point, safe_area.anchor)
            for _ in range(points_in_sa_pc):
                long, lat = DistanceCalculator.shift_point_with_bearing(safe_area_point, random.randint(1,200), random.randint(0,359))
                safe_area.add_to_point_cloud(Point(long, lat))

        # Calculate the total number of deepcopies needed
        rounds = 5
        iterations = 3
        warmup_rounds = 2
        total_iterations = (rounds + warmup_rounds) * iterations + 1

        # Pre-create deepcopies of trajectory
        list_of_safe_areas = [deepcopy(grid_system.safe_areas) for _ in range(total_iterations)]

        # Index to track the current deepcopy to use
        index = [0]

        def update_safe_area_wrapper():
            current_safe_areas = list_of_safe_areas[index[0]]
            update_safe_area(current_safe_areas, grid_system.initialization_point, old_smoothed_main_route)
            index[0] += 1
#
        benchmark.pedantic(update_safe_area_wrapper, rounds=rounds, iterations=iterations, warmup_rounds=warmup_rounds)
#
    @pytest.fixture
    def block_point_cloud(self):
        min_long, min_lat = (0,1)
        point_cloud = TrajectoryPointCloud()

        trajectory = Trajectory()
        current_long = min_long
        current_lat = min_lat

        for i in range(8):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)
        
        for i in range(1, 46):
            current_long = min_long + i * 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(1, 8):
            current_lat = current_lat + 0.0001
            trajectory.add_point(current_long, current_lat)

        point_cloud.add_trajectory(trajectory)
        
        trajectory = Trajectory()
        current_long = min_long
        current_lat = min_lat

        for i in range(16):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)
        
        for i in range(1, 46):
            current_long = min_long + i * 0.0001
            trajectory.add_point(current_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        trajectory = Trajectory()
        current_long = min_long
        current_lat = min_lat
        
        for i in range(46):
            current_long = min_long + i * 0.0001
            trajectory.add_point(current_long, current_lat)

        for i in range(1, 16):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        trajectory = Trajectory()
        current_long = min_long
        current_lat = min_lat

        for i in range(8):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)
        
        for i in range(1, 23):
            current_long = min_long + i * 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(0, 8):
            current_lat = current_lat + 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(0, 23):
            current_long = current_long + 0.0001
            trajectory.add_point(current_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        trajectory = Trajectory()
        current_long = min_long + 45 * 0.0001
        current_lat = min_lat

        for i in range(8):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(current_long, current_lat)
        
        for _ in range(1, 23):
            current_long = current_long - 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(0, 8):
            current_lat = current_lat + 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(1, 23):
            current_long = current_long - 0.0001
            trajectory.add_point(current_long, current_lat)

        point_cloud.add_trajectory(trajectory)


        trajectory = Trajectory()
        current_long = min_long + 45 * 0.0001
        current_lat = min_lat
        
        for _ in range(1, 23):
            current_long = current_long - 0.0001
            trajectory.add_point(current_long, current_lat)

        for i in range(1, 8):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(1, 23):
            current_long = current_long - 0.0001
            trajectory.add_point(current_long, current_lat)

        for _ in range(0, 8):
            current_lat = current_lat + 0.0001
            trajectory.add_point(current_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        trajectory = Trajectory()
        current_long = min_long
        current_lat = min_lat + 7 * 0.0001

        for i in range(1, 46):
            current_long = min_long + i * 0.0001
            trajectory.add_point(current_long, current_lat)

        point_cloud.add_trajectory(trajectory)


        trajectory = Trajectory()
        current_long = min_long
        current_lat = min_lat
 
        for i in range(1, 16):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        trajectory = Trajectory()
        current_long = min_long + 12 * 0.0001
        current_lat = min_lat
 
        for i in range(1, 16):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        trajectory = Trajectory()
        current_long = min_long + 25 * 0.0001
        current_lat = min_lat
 
        for i in range(1, 16):
            current_lat = min_lat + i * 0.0001
            trajectory.add_point(min_long, current_lat)

        point_cloud.add_trajectory(trajectory)

        return point_cloud