""" Program entrypoint """
import database.db as db
import time
from database.taxi_data_handler import TaxiDataHandler
from database.load_data import load_data_from_csv

db_pool = db.init_db()
start_time = time.time()
load_data_from_csv(db_pool)
end_time = time.time()

elapsed_time = end_time - start_time

print("Copied data in {:.5f} seconds".format(elapsed_time))

tdh = TaxiDataHandler(db_pool)
data1 = tdh.read_records_by_trajectory_id(1)
data2 = tdh.read_records_by_trajectory_id(2)

print(data1)
print(data2)
