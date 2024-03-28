from DTC.gridsystem import GridSystem
from database.taxi_data_handler import TaxiDataHandler
from database.load_data import load_data_from_csv
from database.db import init_db, new_tdrive_db_pool

class DTCExecutor:
    def __init__(self, initialize_db: bool = False) -> None:
        if initialize_db:
            connection = init_db()
            load_data_from_csv(connection)
        else:
            connection = new_tdrive_db_pool

        self.tdrive_handler = TaxiDataHandler(connection)
        self.grid_system = None

    def execute_dtc_with_n_points(self, n: int):
        pass
        