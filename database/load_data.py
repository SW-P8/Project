""" Copies the data from csv files into our database """
import os
import pandas as pd
from psycopg2.pool import SimpleConnectionPool
from tqdm import tqdm
from pathlib import Path
from io import StringIO

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
    
    trajectory_id = 1
    file_list = sorted(os.listdir(CSV_DIR), key=__get_numeric_part)

    for filename in tqdm(file_list, desc="Processing Files", unit="file"):
        file = Path(filename)

        if os.path.isfile(file):  # Check if file
            df = pd.read_csv(file, names=['taxi_id', 'date_time', 'longitude', 'latitude'], parse_dates=['date_time'], date_format='%Y-%m-%d %H:%M:%S')

            if not df.empty:
                buffer = StringIO()
                transform_data(df, trajectory_id).to_csv(buffer, index=False, sep=',')
                buffer.seek(0)

                cursor.copy_expert(COPY_STATEMENT, buffer)

                # Update trajectory ID globaly
                trajectory_id = df['trajectory_id'].max() + 1

    conn.commit()
    cursor.close()
    db.putconn(conn)


def __get_numeric_part(file_name) -> int:
    return int(file_name.split('/')[-1].split('.')[0])

def transform_data(df: pd.DataFrame, trajectory_id: int) -> pd.DataFrame:
    valid_longitude = (115.42, 117.51) # South, North bounds for Beijing
    valid_latitude = (39.44, 41.06) # West, East vounds for Beijing

    mask = (
        (df['longitude'] < valid_longitude[0]) |
        (df['longitude'] > valid_longitude[1]) |
        (df['latitude'] < valid_latitude[0]) |
        (df['latitude'] > valid_latitude[1])
    )

    df.sort_values(by='date_time', inplace=True)
    df.drop_duplicates(inplace=True)
    df['time_diff'] = df['date_time'].diff().fillna(pd.Timedelta(seconds=0))
    df['trajectory_id'] = ((df['time_diff'].dt.total_seconds() / 60) > 12).cumsum() + trajectory_id
    df = df.drop(columns=['time_diff'])
    df = df[~mask]



    return df
