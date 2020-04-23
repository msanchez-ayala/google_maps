import psycopg2
from sql_queries import create_table_queries, drop_table_queries, trips_time_create


def create_database():
    """
    Returns
    -------
    psycopg2 cursor and connection objects.

    A connection is established with the default database. google_maps is
    dropped if it exists, and is then created. The connection to the default
    database is closed, and a new connection is establised with google_maps.
    """

    # connect to default database
    conn = psycopg2.connect(
        host = '127.0.0.1',
        dbname = 'defaultdb',
        user = 'google_user',
        password = 'passw0rd',
    )
    cur = conn.cursor()
    conn.set_session(autocommit = True)

    # create sparkify database with UTF8 encoding
    cur.execute("DROP DATABASE IF EXISTS google_maps")
    cur.execute("CREATE DATABASE google_maps WITH ENCODING 'utf8' TEMPLATE template0")

    # close connection to default database
    conn.close()

    # connect to google_maps database
    conn = psycopg2.connect(
        host = '127.0.0.1',
        dbname = 'google_maps',
        user = 'google_user',
        password = 'passw0rd'
    )
    cur = conn.cursor()
    conn.set_session(autocommit = True)

    return cur, conn


def drop_tables(cur):
    """
    All tables in google_maps are dropped as specified by the queries in
    sql_queries.py.
    """
    for query in drop_table_queries:
        try:
            cur.execute(query)
        except psycopg2.Error as e:
            print('ERROR: Could not drop table')
            print(e)


def create_tables(cur):
    """
    All tables in google_maps are created as specified by the queries in
    sql_queries.py.
    """
    for query in create_table_queries:
        try:
            cur.execute(query)
        except psycopg2.Error as e:
            print('ERROR: Could not create table')
            print(e)


def create_view(cur):
    """
    Creates the view that joins trips and time tables for the app.
    """
    try:
        cur.execute(trips_time_create)
    except psycopg2.Error as e:
        print('ERROR: Could not create the view')
        print(e)

def main():
    """
    Bundles up the script: creates db and opens connection, drops all tables
    that exist, creates all five tables, and then closes the connection to the
    database.
    """
    cur, conn = create_database()

    drop_tables(cur)
    create_tables(cur)
    create_view(cur)

    conn.close()


if __name__ == "__main__":
    main()
