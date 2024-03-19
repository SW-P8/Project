"""
Module for handling CRUD operations on TaxiData table.
"""

class TaxiDataHandler:
    """
    A class to perform CRUD operations on TaxiData table.
    """
    def __init__(self, connection_pool):
        """
        Constructor for TaxiDataHandler.

        Args:
            connection_pool: psycopg2 connection pool object.
        """
        self.__connection_pool = connection_pool

    def create_record(self, taxi_id, date_time, longitude, latitude, trajectory_id):
        """
        Creates a new record in the TaxiData table.

        Args:
            taxi_id: Integer, taxi ID.
            date_time: Datetime object, date and time of the record.
            longitude: Float, longitude coordinate.
            latitude: Float, latitude coordinate.
            trajectory_id: Integer, trajectory ID.
        """
        sql = "INSERT INTO TaxiData (taxi_id, date_time, longitude, latitude, trajectory_id) VALUES (%s, %s, %s, %s, %s)"
        with self.__connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (taxi_id, date_time, longitude, latitude, trajectory_id))
                conn.commit()

    def read_records_by_taxi_id(self, taxi_id):
        """
        Retrieves all records from the TaxiData table associated with the specified taxi ID.

        Args:
            taxi_id: Integer, taxi ID.

        Returns:
            List of tuples containing records associated with the specified taxi ID.
        """
        sql = "SELECT * FROM TaxiData WHERE taxi_id = %s"
        with self.__connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (taxi_id,))
                return cursor.fetchall()
                
    def read_records_by_trajectory_id(self, trajectory_id):
        """
        Retrieves records from the TaxiData table by trajectory ID.

        Args:
            trajectory_id: Integer, trajectory ID.

        Returns:
            List of tuples containing records associated with the specified trajectory ID.
        """
        sql = "SELECT * FROM TaxiData WHERE trajectory_id = %s"
        with self.__connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (trajectory_id,))
                return cursor.fetchall()

    def update_record(self, taxi_id, new_date_time, new_longitude, new_latitude, new_trajectory_id):
        """
        DO NOT USE THIS METHOD SINCE TAXI_ID IS NOT A UNIQUE IDENTIFIER. Updates a record in the TaxiData table.

        Args:
            taxi_id: Integer, taxi ID of the record to be updated.
            new_date_time: Datetime object, new date and time value.
            new_longitude: Float, new longitude coordinate.
            new_latitude: Float, new latitude coordinate.
            new_trajectory_id: Integer, new trajectory ID.
        """
        sql = "UPDATE TaxiData SET date_time = %s, longitude = %s, latitude = %s, trajectory_id = %s WHERE taxi_id = %s"
        with self.__connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (new_date_time, new_longitude, new_latitude, new_trajectory_id, taxi_id))
                conn.commit()

    def delete_taxi_records(self, taxi_id):
        """
        Deletes all trajectories for a taxi
        Args:
            taxi_id: Integer, taxi ID of the trajectory records to be deleted.
        """
        sql = "DELETE FROM TaxiData WHERE taxi_id = %s"
        with self.__connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (taxi_id,))
                conn.commit()
    
    def delete_trajectory_records(self, trajectory_id):
        """
        Deletes all datapoints for a trajectories
        Args:
            taxi_id: Integer, trajectory ID of the trajectory datapoint records to be deleted.
        """
        sql = "DELETE FROM TaxiData WHERE trajectory_id = %s"
        with self.__connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (trajectory_id,))
                conn.commit()

