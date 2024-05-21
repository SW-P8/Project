import config
from DTC.gridsystem import GridSystem
from DTC.dtc_executor import DTCExecutor
from database.taxi_data_handler import TaxiDataHandler
from visuals.visualizer import Visualizer
from database.db import init_db, new_tdrive_db_pool
from DTC.trajectory import Trajectory, TrajectoryPointCloud

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
db_conn = TaxiDataHandler(init_db())
data = db_conn.execute_query("SELECT * FROM taxidate where longitude > 116.2031 AND longitude < 116.5334 AND latitude > 39.7513 AND latitude < 40.0245 AND date_time <= '2008-02-04 20:35:22';")
# 2. Smid 50% af trajectories ind i modellen
pc = create_point_cloud(data)
gs = GridSystem(pc)
gs.create_grid_system()
gs.extract_main_route()
gs.extract_route_skeleton()
gs.construct_safe_areas()

count_safe_areas = len(gs.safe_areas)
# 3. Smid resten ind i et increments
# second_half_points = 
second_half = db_conn.execute_query("SELECT * FROM taxidate where longitude > 116.2031 AND longitude < 116.5334 AND latitude > 39.7513 AND latitude < 40.0245 AND date_time > '2008-02-04 20:35:22';")

# 4. Mål hvor mange punkter der bliver fjernet fra modellen pga time decay
# 5. Juster time decay så vi får et antal punkter der giver mening

