import os
import warnings
import pandas as pd
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from DTC.gridsystem import GridSystem

warnings.simplefilter(action='ignore', category=UserWarning)
CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS DTC_model_min_coords (
        model_id SERIAL PRIMARY KEY,
        min_longitude FLOAT NOT NULL,
        min_latitude FLOAT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DTC_model_safe_areas (
        area_id SERIAL PRIMARY KEY,
        model_id INT NOT NULL,
        anchor_x FLOAT NOT NULL,
        anchor_y FLOAT NOT NULL,
        radius FLOAT NOT NULL,
        FOREIGN KEY (model_id) REFERENCES DTC_model_min_coords(model_id) ON DELETE CASCADE
    );
    """
]

def insert_safe_areas(model_id, safe_areas, cursor, conn):
    sql = """
    INSERT INTO DTC_model_safe_areas (model_id, anchor_x, anchor_y, radius)
    VALUES (%s, %s, %s, %s);
    """
    params = [(model_id, anchor_x, anchor_y, radius) for anchor_x, anchor_y, radius in safe_areas]
    try:
        cursor.executemany(sql, params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
        
def insert_long_lat(min_longitude, min_latitude, conn, cursor):
    """Insert a new model instance and return its model_id"""
    sql = """
    INSERT INTO DTC_model_min_coords (min_longitude, min_latitude)
    VALUES (%s, %s) RETURNING model_id;
    """
    model_id = None
    try:
        cursor.execute(sql, (min_longitude, min_latitude))
        model_id = cursor.fetchone()[0]
        conn.commit()  
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return model_id


def save_data(gs: GridSystem, db: SimpleConnectionPool):
    # Get safe_areas
    safe_areas = gs.safe_areas
    # Get min_long_lat
    min_long_lat = gs.pc.get_shifted_min()
    
    try:
        conn = db.getconn()
        cursor = conn.cursor()
        for sql_cmd in CREATE_TABLES_SQL:
            cursor.execute(sql_cmd)
        id = insert_long_lat(min_long_lat[0], min_long_lat[1], conn, cursor)
        insert_safe_areas(id, safe_areas, cursor, conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    
        
    

