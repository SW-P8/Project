""" This module handles database creation, connection and dev seed for testing. """
import os
from psycopg2.pool import SimpleConnectionPool
from psycopg2 import sql
PG_HOST = "localhost"
PG_ROOT_DB = "postgres"
PG_ROOT_USER = "postgres"
PG_ROOT_PWD = "postgres"
SQL_RECREATE = "sql/00-recreate-db.sql"

PG_TDRIVE_DB = "tdrive_db"
PG_TDRIVE_USER = "tdrive_user"
PG_TDRIVE_PWD = "tdrivepass"
PG_TDRIVE_MAX_CON = 5

def init_db() -> SimpleConnectionPool:
    """ Initializes database and creates a connection pool for use in the application """
    # Create the db with PG_ROOT (dev only)
    root_db = __new_db_pool(PG_HOST, PG_ROOT_DB, PG_ROOT_USER, PG_ROOT_PWD, 1)
    __pexec(root_db, SQL_RECREATE)

    # Get the sql files
    app_db = __new_db_pool(PG_HOST, PG_TDRIVE_DB, PG_TDRIVE_USER, PG_TDRIVE_PWD, PG_TDRIVE_MAX_CON)
    paths = [os.path.join("sql/", filename) for filename in os.listdir("sql/")]
    paths = [os.path.abspath(path) for path in paths if os.path.isfile(path)]
    paths.sort()

    # Execute each file
    for path in paths:
        if path.endswith('.sql') and not SQL_RECREATE in path:
            __pexec(app_db, path)

    return __new_db_pool(PG_HOST, PG_TDRIVE_DB, PG_TDRIVE_USER, PG_TDRIVE_PWD, PG_TDRIVE_MAX_CON)

def __pexec(db: SimpleConnectionPool, file):
    """ Executes sql statements from a file """
    # Read the file
    content: str = ""
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as ex:
        print(f"ERROR reading {file} (cause: {ex})")
        raise ex

    # Split SQL statements using semicolons, remove leading/trailing whitespace and empty statements
    sql_statements = content.split(';')
    sql_statements = [statement.strip() for statement in sql_statements]
    sql_statements = [statement for statement in sql_statements if statement]

    conn = db.getconn()
    conn.autocommit = True # Execute commands outside of a transaction block
    cursor = conn.cursor()
    for sql_statement in sql_statements:
        cursor.execute(sql.SQL(sql_statement))

    cursor.close()
    db.putconn(conn)

def __new_db_pool(host: str, db: str, user: str, pwd: str, max_con: int) -> SimpleConnectionPool:
    """ Creates a database connection pool """
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=max_con,
        host=host,
        database=db,
        user=user,
        password=pwd
    )

    return pool
