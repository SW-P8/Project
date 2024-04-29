from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from database.taxi_data_handler import TaxiDataHandler
from database.load_data import load_data_from_csv
from database.db import init_db, new_tdrive_db_pool

class DTCExecutor:
    def __init__(self, initialize_db: bool = False) -> None:
        if initialize_db:
            connection = init_db()
            load_data_from_csv(connection)
        else:
            connection = new_tdrive_db_pool()

        self.tdrive_handler = TaxiDataHandler(connection)
        self.grid_system = None

    def execute_dtc_with_n_points(self, n: int):
        pc = self.create_point_cloud_with_n_points(n)
        gs = GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()
        gs.extract_route_skeleton()
        gs.construct_safe_areas()

        #TODO: Implement online step

        return gs
    
    def create_point_cloud_with_n_points(self, n: int):
        records = self.tdrive_handler.read_n_records_inside_bbb(n)
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
        
