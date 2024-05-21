import config
from DTC.gridsystem import GridSystem
from DTC.dtc_executor import DTCExecutor
from database.taxi_data_handler import TaxiDataHandler
from visuals.visualizer import Visualizer
from database.db import init_db, new_tdrive_db_pool
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.json_read_write import read_safe_areas_from_json, write_safe_areas_to_json, read_point_cloud_from_json, write_point_cloud_to_json, read_set_of_tuples_from_json, write_set_of_tuples_to_json
from onlinedtc.onlinerunner import RunCleaning
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_main_route import ConstructMainRoute
from DTC.construct_safe_area import ConstructSafeArea
from math import ceil
import os


def create_point_cloud(records):
    tid_of_existing_trajectory = 1
    trajectory = Trajectory()
    pc = TrajectoryPointCloud()

    for _, timestamp, longitude, latitude, tid in records:
        # Separate points into trajectories based on their trajectory ids
        if tid != tid_of_existing_trajectory:
            pc.add_trajectory(trajectory)
            trajectory = Trajectory()
            tid_of_existing_trajectory = tid
        trajectory.add_point(longitude, latitude, timestamp)
    pc.add_trajectory(trajectory)
    return pc

# 1. Sorter trajectories by time, brug det sidste punkts tidspunkt i et trajectory. Median time: '2008-02-04 23:26:44' found using scientific querying
# 2. Smid 50% af trajectories ind i modellen
def load_initial_model():
    print('    Loading point cloud ...')
    if os.path.exists("first_half_smr.json"):
        smoothed_main_route = read_set_of_tuples_from_json("first_half_smr.json")
        safe_areas = read_safe_areas_from_json("first_half_sa.json")
        initialization_point = read_set_of_tuples_from_json("first_half_initpoint.json")
        return smoothed_main_route, safe_areas, tuple(initialization_point)

    if not os.path.exists("first_half_pc.json"):
        db_conn = TaxiDataHandler(new_tdrive_db_pool())
        data = db_conn.execute_query("SELECT * FROM taxidata where longitude > 116.2031 AND longitude < 116.5334 AND latitude > 39.7513 AND latitude < 40.0245 AND date_time <= '2008-02-04 20:35:22' order by date_time")
        pc = create_point_cloud(data)
        write_point_cloud_to_json("first_half_pc.json", pc)
    else:
        pc = read_point_cloud_from_json("first_half_pc.json")

    gs = GridSystem(pc)
    gs.create_grid_system()
    print(gs.initialization_point)
    main_route = ConstructMainRoute.extract_main_route(gs.grid)
    smoothed_main_route = RouteSkeleton.smooth_main_route(main_route)
    filtered_main_route = RouteSkeleton.graph_based_filter(smoothed_main_route, config.filtering_list_radius, ceil(0.0001 * len(main_route)))
    route_skeleton = RouteSkeleton.filter_sparse_points(filtered_main_route)
    safe_areas = ConstructSafeArea.construct_safe_areas(route_skeleton, gs.grid)
    
    write_set_of_tuples_to_json("first_half_smr.json", smoothed_main_route)
    write_set_of_tuples_to_json("first_half_initpoint.json", gs.initialization_point)
    write_safe_areas_to_json("first_half_sa.json", safe_areas)
    return smoothed_main_route, safe_areas, gs.initialization_point

def load_point_cloud():
    if os.path.exists("second_half.json"):
        return read_point_cloud_from_json("second_half.json")
    db_conn = TaxiDataHandler(new_tdrive_db_pool())
    data = db_conn.execute_query("SELECT * FROM taxidata where longitude > 116.2031 AND longitude < 116.5334 AND latitude > 39.7513 AND latitude < 40.0245 AND date_time > '2008-02-04 20:35:22' order by date_time")
    pc = create_point_cloud(data)
    del pc.trajectories[0]
    write_point_cloud_to_json("second_half.json", pc)
    return pc

print('Loading first half of point cloud ...')
smoothed_main_route, safe_areas, initialization_point = load_initial_model()

print('Loading second half of point cloud ...')
# 3. Smid resten ind i et increments
pc = load_point_cloud()

print('Running incremental ...')
print('    Creating run cleaning object ...')
print(f'    Number of safe areas before incremental: {len(safe_areas)}')
increment_runner = RunCleaning(safe_areas, initialization_point, smoothed_main_route)
print('    I1nserting point cloud ...')
increment_runner.read_trajectories(pc)
print('    Cleaning and incrementing ...')
increment_runner.clean_and_increment()
print(f'    Number of safe areas after incremental: {len(increment_runner.safe_areas)}')

# 4. Mål hvor mange punkter der bliver fjernet fra modellen pga time decay
# 5. Juster time decay så vi får et antal punkter der giver mening
