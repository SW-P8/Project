""" Copies the data from csv files into our database """
import os
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
import pandas as pd
from psycopg2.pool import SimpleConnectionPool
from tqdm import tqdm
from pathlib import Path
from io import StringIO

BBB_MIN_LONG = 115.42
BBB_MAX_LONG = 117.51
BBB_MIN_LAT = 39.44
BBB_MAX_LAT = 41.06

CSV_DIR = "taxi_log_2008_by_id/"
COPY_STATEMENT = """
    COPY TaxiData(taxi_id, date_time, longitude, latitude, trajectory_id)
    FROM STDIN
    DELIMITER ','
    CSV HEADER
"""

def load_data_from_csv(db: SimpleConnectionPool, limit=0):
    """ Loads data from csv file into databases """
    conn = db.getconn()
    cursor = conn.cursor()
    
    trajectory_id = 1
    file_list = sorted(os.listdir(CSV_DIR), key=__get_numeric_part)
    file_list = file_list[:limit] if limit > 0 else file_list

    for filename in tqdm(file_list, desc="Processing Files", unit="file"):
        file = CSV_DIR + filename

        if os.path.isfile(file):
            df = pd.read_csv(file, names=['taxi_id', 'date_time', 'longitude', 'latitude'], parse_dates=['date_time'], date_format='%Y-%m-%d %H:%M:%S')

            if not df.empty:
                buffer = StringIO()
                __transform_data(df, trajectory_id).to_csv(buffer, index=False, sep=',')
                buffer.seek(0)

                cursor.copy_expert(COPY_STATEMENT, buffer)

                # Update trajectory ID globaly
                trajectory_id = df['trajectory_id'].max() + 1

    conn.commit()
    cursor.close()
    db.putconn(conn)

def __get_numeric_part(file_name) -> int:
    return int(file_name.split('/')[-1].split('.')[0])

def __transform_data(df: pd.DataFrame, trajectory_id: int, inner_city: bool = False) -> pd.DataFrame:
    if inner_city:
        min_long = 116.342222
        max_long = 116.436389
        min_lat = 39.866389
        max_lat = 39.983056
    else:
        min_long = 115.42
        max_long = 117.51
        min_lat = 39.44
        max_lat = 41.06

    mask = ~(
        (df['longitude'] < min_long) |
        (df['longitude'] > max_long) |
        (df['latitude'] < min_lat) |
        (df['latitude'] > max_lat)
    )

    df.sort_values(by='date_time', inplace=True)
    df.drop_duplicates(inplace=True)
    df['time_diff'] = df['date_time'].diff().fillna(pd.Timedelta(seconds=0))
    df['trajectory_id'] = ((df['time_diff'].dt.total_seconds() / 60) > 12).cumsum() + trajectory_id
    df = df.drop(columns=['time_diff'])
    df.reset_index(drop=True, inplace=True)
    df = df[mask]

    return df
