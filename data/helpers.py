"""
HELPER FUNCTIONS
"""

# write a function to insert data into the reviews table
def insert_trip_data(trip_objects, cursor, cnx):
    """
    Inserts data into google_maps.trips table.
    
    PARAMETERS
    ----------
    
    trip_object: List of 2 GDirections trip objects containing information 
                 to be inserted into the MySQL table. First object contains
                 info from my house to gf and second object is the other trip.
    """
    # Create list of tuples for the objects in trip_objects
    trip_tuples = [
        (
        trip_object.get_trip_start(),         # departure_time
        i,                                    # trip_direction (either 0 or 1)
        trip_object.get_trip_duration(),      # trip_duration
        )
        for i, trip_object in enumerate(trip_objects)
    ]
       
    insert_statement = """
                       INSERT INTO 
                         google_maps.trips (departure_time, trip_direction, trip_duration) 
                       VALUES 
                         (%s, %s, %s)
                       ;"""
    cursor.executemany(insert_statement,trip_tuples)
    cnx.commit()
    
def insert_instructions_data(trip_objects, cursor, cnx):
    """
    Inserts data into google_maps.instructions table.
    
    PARAMETERS
    ----------
    
    trip_object: List of 2 GDirections trip objects containing information 
                 to be inserted into the MySQL table. First object contains
                 info from my house to gf and second object is the other trip.
    """
    final_tuples = []
    
    # Start by iterating through trip_objects
    for i, trip_object in enumerate(trip_objects):
        
        # Create list of tuples for the objects in trip_objects
        instructions_tuples = [
            (
                trip_object.get_trip_start(),    # departure_time
                i,                               # trip_direction (either 0 or 1)
                trip_step['step'],               # trip_setp
                trip_step['travel_mode'],        # transit_line
                trip_step['length']             # step_duration
            )
            for trip_step in trip_object.get_trip_instructions()
        ]
        
        # Append to final_tuples list
        final_tuples.extend(instructions_tuples)
       
    insert_statement = """
                       INSERT INTO 
                         google_maps.instructions (departure_time, trip_direction, trip_step, transit_line, step_duration) 
                       VALUES 
                         (%s, %s, %s, %s, %s)
                       ;"""
    cursor.executemany(insert_statement,final_tuples)
    cnx.commit()
