""" Copies the data from csv files into our database """
import os
import pandas as pd
from psycopg2.pool import SimpleConnectionPool
from tqdm import tqdm
from pathlib import Path

CSV_DIR = "taxi_log_2008_by_id/"
COPY_STATEMENT = """
    COPY TaxiData(taxi_id, date_time, longitude, latitude, trajectory_id)
    FROM STDIN
    DELIMITER ','
    CSV HEADER
"""


def load_data_from_csv(db: SimpleConnectionPool):
    """ Loads data from csv file into databases """
    conn = db.getconn()
    cursor = conn.cursor()
    
    trajectory_id = 0
    file_list = sorted(os.listdir(CSV_DIR), key=__get_numeric_part)

    for filename in tqdm(file_list, desc="Processing Files", unit="file"):
        file = Path(CSV_DIR) / filename

        if os.path.isfile(file):  # Check if file
            df = pd.read_csv(file, names=[
                             'taxi_id', 'date_time', 'longitude', 'latitude'], parse_dates=['date_time'])

            if not df.empty:
                df.sort_values(by='date_time', inplace=True)
                df.drop_duplicates(inplace=True)
                df['time_diff'] = (
                    df['date_time'] - df['date_time'].shift().fillna(pd.Timedelta(seconds=0)))
                df['trajectory_id'] = (df['time_diff'] > pd.Timedelta(
                    minutes=12)).cumsum() + trajectory_id
                df = df.drop(columns=['time_diff'])

                cursor.copy_expert(COPY_STATEMENT, df.to_csv(
                    index=False, sep='\t', header=True) + '\n')

                # Update trajectory ID globaly
                trajectory_id = df['trajectory_id'].max() + 1

    conn.commit()
    cursor.close()
    db.putconn(conn)


def __get_numeric_part(file_name) -> int:
    return int(file_name.split('/')[-1].split('.')[0])