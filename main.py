""" Program entrypoint """
import database.db as db
import time
from database.load_data import load_data_from_csv

db_pool = db.init_db()
start_time = time.time()
load_data_from_csv(db_pool)
end_time = time.time()

elapsed_time = end_time - start_time

print("Copied data in {:.5f} seconds".format(elapsed_time))