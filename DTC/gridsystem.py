from DTC.trajectory import TrajectoryPointCloud, Trajectory
from scipy.spatial import KDTree
from DTC.distance_calculator import DistanceCalculator
from math import floor
from collections import defaultdict
import multiprocessing as mp
from DTC.construct_safe_area import ConstructSafeArea
from DTC.construct_main_route import ConstructMainRoute
from DTC.route_skeleton import RouteSkeleton
from DTC.incremental import Incremental
from math import floor
from DTC.collection_utils import CollectionUtils

class GridSystem:
    def __init__(self, pc: TrajectoryPointCloud) -> None:
        self.pc = pc
        self.initialization_point = pc.get_shifted_min()
        self.grid = defaultdict(list)
        self.main_route = set()
        self.route_skeleton = set()
        self.safe_areas = defaultdict(set)
        self.safe_areas_list = list()
        self.safe_area_trees = KDTree

    def create_grid_system(self):
        process_count = mp.cpu_count()
        splits = CollectionUtils.split(self.pc.trajectories, process_count)
        tasks = []
        pipe_list = []

        for split in splits:
            if split != []:
                recv_end, send_end = mp.Pipe(False)
                t = mp.Process(target=self.create_sub_grid, args=(split, send_end))
                tasks.append(t)
                pipe_list.append(recv_end)
                t.start()

        # Receive subgrids from processes and merge
        merged_dict = defaultdict(list)
        for (i, task) in enumerate(tasks):
            d = pipe_list[i].recv()
            task.join()
            for key, value in d.items():
                merged_dict[key].extend(value)

        self.grid = merged_dict

    def create_sub_grid(self, trajectories: list[Trajectory], send_end) -> dict:
        sub_grid = defaultdict(list)
        for trajectory in trajectories:
            for point in trajectory.points:
                (x,y) = DistanceCalculator.calculate_exact_index_for_point(point, self.initialization_point)
                floored_index = (floor(x), floor(y))
                sub_grid[floored_index].append((x,y))
        
        send_end.send(sub_grid)

    def extract_main_route(self, distance_scale: float = 0.2):
        self.main_route = ConstructMainRoute.extract_main_route(self.grid, distance_scale)
    
    def extract_route_skeleton(self, smooth_radius: int = 25, filtering_list_radius: int = 20, distance_interval: int = 20):
        self.route_skeleton = RouteSkeleton.extract_route_skeleton(self.main_route, smooth_radius, filtering_list_radius, distance_interval)

    def construct_safe_areas(self, decrease_factor: float = 0.01):
        self.safe_areas = ConstructSafeArea.construct_safe_areas(self.route_skeleton, self.grid, decrease_factor, self.initialization_point)
        self.construct_safe_areas_tree()
    
    def construct_safe_areas_tree(self):
        if self.safe_areas is None:
            return
        self.safe_areas_list = list(self.safe_areas.keys())
        self.safe_area_trees = KDTree(self.safe_areas_list)


    def incremental_refinement(self, pc: TrajectoryPointCloud):
        inc = Incremental(self.safe_areas)
        for trajectory in pc.trajectories:
            for p in trajectory.points:
                inc.incremental_refine(p, self.initialization_point)