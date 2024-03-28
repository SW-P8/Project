from DTC.gridsystem import GridSystem
from DTC.trajectory import Trajectory, Point, TrajectoryPointCloud
from database.taxi_data_handler import TaxiDataHandler
from database.load_data import load_data_from_csv
from database.db import init_db, new_tdrive_db_pool
import time

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
        records = self.tdrive_handler.read_n_records(n)
        tid_of_existing_trajectory = 1
        trajectory = Trajectory()
        pc = TrajectoryPointCloud()

        start_time = time.time()
        for _, timestamp, longitude, latitude, tid in records:
            if tid != tid_of_existing_trajectory:
                pc.add_trajectory(trajectory)
                trajectory = Trajectory()

            trajectory.add_point(longitude, latitude, timestamp)
        end_time = time.time()
        print("Trajectory point cloud creation completed in {:.5f} seconds".format(end_time - start_time))


        gs = GridSystem(pc)
        start_time = time.time()
        gs.create_grid_system()
        end_time = time.time()
        print("Grid system creation completed in {:.5f} seconds".format(end_time - start_time))


        start_time = time.time()
        gs.extract_main_route()
        end_time = time.time()
        print("Main route extraction completed in {:.5f} seconds".format(end_time - start_time))


        start_time = time.time()
        gs.extract_route_skeleton()
        end_time = time.time()
        print("Route skeleton extraction completed in {:.5f} seconds".format(end_time - start_time))


        start_time = time.time()
        gs.construct_safe_areas()
        end_time = time.time()
        print("Safe area construction completed in {:.5f} seconds".format(end_time - start_time))

        return gs
        