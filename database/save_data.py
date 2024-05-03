import psycopg2
from psycopg2.pool import SimpleConnectionPool
from DTC.gridsystem import GridSystem

#warnings.simplefilter(action='ignore', category=UserWarning)

def insert_safe_areas(model_id, safe_areas, cursor, conn):
    """
    Bulk inserts multiple safe areas for a given model instance into the database.

    Args:
        model_id (int): The ID of the model instance to which the safe areas belong.
        safe_areas (list of tuples): A list where each tuple contains the details of a safe area (anchor_x, anchor_y, radius).
        cursor (psycopg2.cursor): A cursor object obtained from a psycopg2 connection to execute PostgreSQL commands.
        conn (psycopg2.connection): A connection object to the PostgreSQL database.

    The function commits the transaction if all inserts succeed, otherwise, it prints the error.
    """
    sql = """
    INSERT INTO DTC_model_safe_areas (model_id, anchor_x, anchor_y, radius)
    VALUES (%s, %s, %s, %s);
    """
    params = [(model_id, value.anchor[0], value.anchor[1], value.radius) for _, value in safe_areas.items()]
    
    try:
        cursor.executemany(sql, params)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("insert save_area errrors" ,error)
        
        
def insert_long_lat(min_longitude, min_latitude, conn, cursor):
    """
    Inserts a new model instance's minimum longitude and latitude into the database and returns the generated model_id.

    Args:
        min_longitude (float): The minimum longitude value of the model instance.
        min_latitude (float): The minimum latitude value of the model instance.
        conn (psycopg2.connection): A connection object to the PostgreSQL database.
        cursor (psycopg2.cursor): A cursor object obtained from a psycopg2 connection to execute PostgreSQL commands.

    Returns:
        model_id (int): The auto-generated ID of the newly inserted model instance. Returns None if the insert fails.
    """
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
        print("insert_long_lat_error", error)
    return model_id


def save_data(gs: GridSystem, db: SimpleConnectionPool):
    """
    Saves data related to a GridSystem instance into the database using a connection pool.

    Args:
        gs (GridSystem): An instance of the GridSystem class containing the data to be saved.
        db (SimpleConnectionPool): A psycopg2 pool object to manage database connections.

    This function first inserts the minimum longitude and latitude of the GridSystem instance,
    retrieves the generated model_id, and then uses this id to bulk insert safe areas associated
    with the GridSystem into the database. It commits the transaction upon success or prints
    the error if something goes wrong. Finally, it ensures the database connection is closed.
    """
    # Get safe_areas
    safe_areas = gs.safe_areas
    # Get min_long_lat
    min_long_lat = gs.pc.get_shifted_min()
    
    try:
        conn = db.getconn()
        cursor = conn.cursor()
        id = insert_long_lat(min_long_lat[0], min_long_lat[1], conn, cursor)
        insert_safe_areas(id, safe_areas, cursor, conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print("error in main",error)
    finally:
        if conn is not None:
            conn.close()
