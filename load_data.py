""" Copies the data from csv files into our database """
import os
from psycopg2.pool import SimpleConnectionPool
CSV_DIR = "taxi_log_2008_by_id/"
COPY_STATEMENT = """
    COPY TaxiData(taxi_id, date_time, longitude, latitude)
    FROM STDIN
    DELIMITER ','
    CSV HEADER
"""

def load_data_from_csv(db: SimpleConnectionPool):
    """ Loads data from csv file into databases """
    conn = db.getconn()
    cursor = conn.cursor()
    # overvej om det er lidt for overkil at sort og print hver 100...
    for i, filename in enumerate(sorted(os.listdir(CSV_DIR), key=__get_numeric_part)):
        # Check if the current item is a file
        if i % 100 == 0:
            print(filename)
        file = os.path.join(CSV_DIR, filename)
        if os.path.isfile(file):
            __get_numeric_part(file)
            with open(file, 'r', encoding='utf-8') as f:
                cursor.copy_expert(COPY_STATEMENT, f)

    conn.commit()
    cursor.close()
    db.putconn(conn)


def __get_numeric_part(file_name) -> int:
    return int(file_name.split('/')[-1].split('.')[0])  
