"""
HELPER FUNCTIONS
"""

def insert_data(trip_objects, cursor, cnx):
    """
    Inserts data into google_maps MySQL db.

    PARAMETERS
    ----------

    trip_object: List of 2 GDirections trip objects containing information
                 to be inserted into the MySQL table. First object contains
                 info from my house to gf and second object is the other trip.

    cursor: mysql cursor
    cnx: mysql connection
    """
    # Create list of tuples for the objects in trip_objects
    trip_tuples = [
        (
        trip_object.get_trip_start(),         # departure_time
        i,                                    # trip_direction (either 0 or 1)
        trip_object.get_trip_duration(),      # trip_duration
        str(trip_object.get_trip_instructions())   # trip_instructinos
        )
        for i, trip_object in enumerate(trip_objects)
    ]

    insert_statement = """
                       INSERT INTO
                         google_maps.trips (departure_time, trip_direction, trip_duration, trip_instructions)
                       VALUES
                         (%s, %s, %s, %s)
                       ;"""
    cursor.executemany(insert_statement,trip_tuples)
    cnx.commit()
