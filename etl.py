"""
This module calls the Google Maps API, parses information, and stores into
google_maps.trips MySQL db.
"""
from datetime import datetime
import googlemaps
import config
from directions import Directions
import helpers


### EXTRACTION/TRANSFORMATION HELPERS ###


def get_coordinates(address, gmaps):
    """
    Returns
    -------
    Lat/Long corresponding to the supplied address.

    Parameters
    ----------
    address: [str] An address as you would enter it into Google Maps.
    gmaps: [googlemaps.Client object] Client object for current session.

    Examples
    --------
    >>> get_coordinates('One World Trade Center')
    {'lat': 40.7127431, 'lng': -74.0133795}

    >>> get_coordinates('476 5th Ave, New York, NY 10018')
    {'lat': 40.75318230000001, 'lng': -73.9822534}
    """
    geocoded_address = gmaps.geocode(address)
    geometry = geocoded_address[0]['geometry']['location']
    return geometry

def extract_transform_directions(location_1, location_2, key):
    """
    Extracts and transforms data from the Google Maps API trip information
    between location_1 and location_2.

    Returns
    -------
    List of two Directions objects. One for a trip in each direction:

    location_1 -> location 2 AND
    location_2 -> location 1

    Parameters
    ----------
    location_1: [str] First location of this transit trip. An address as you
        would enter it into Google Maps.
    location_2: [str] Second location of this transit trip. An address as you
        would enter it into Google Maps.
    key: [str] Google API key.
    """
    gmaps = googlemaps.Client(key)
    gmaps = googlemaps.Client(config.api_key)

    # Get coordinates for two locations
    location_1_coords = get_coordinates(location_1, gmaps)
    location_2_coords = get_coordinates(location_2, gmaps)

    # Instantiate Direction objects for each trip (class handles extraction
    # and transformation of the data in the __init__ method)
    trip_1 = Directions(
        location_1_coords, location_2_coords, 'transit', gmaps
    )
    trip_2 = Directions(
        location_2_coords, location_1_coords, 'transit', gmaps
    )

    return [trip_1, trip_2]


### LOAD HELPERS ###


def create_trips_tuples(trip_objects):
    """
    Returns
    -------
    List of tuples for insertion into the MySQL db. Each tuple contains the
    departure time, trip direction, and trip duration for each of the two trip
    objects.

    Parameters
    ----------
    trip_objects: List of 2 Directions trip objects containing information
                 to be inserted into the MySQL table. First object contains
                 info from location_1 -> location_2 and second object is the
                 other trip.
    """
    trip_tuples = [
        (
            trip_object.get_trip_start(),       # departure_time
            i,                                  # trip_direction (either 0 or 1)
            trip_object.get_trip_duration(),    # trip_duration
        )
        for i, trip_object in enumerate(trip_objects)
    ]
    return trip_tuples

def create_instructions_tuples(trip_objects):
    """
    Returns
    -------
    List of tuples for insertion into the MySQL db. Each tuple contains the
    departure time, trip direction, trip step, transit line, and step duration
    for each of the two trip objects.

    Parameters
    ----------
    trip_objects: List of 2 Directions trip objects containing information
                 to be inserted into the MySQL table. First object contains
                 info from location_1 -> location_2 and second object is the
                 other trip.
    """
    final_tuples = []

    # Start by iterating through trip_objects
    for i, trip_object in enumerate(trip_objects):

        # Create list of tuples for the objects in trip_objects
        instructions_tuples = [
            (
                trip_object.get_trip_start(),    # departure_time
                i,                               # trip_direction (either 0 or 1)
                trip_step['step'],               # trip_step
                trip_step['travel_mode'],        # transit_line
                trip_step['length']             # step_duration
            )
            for trip_step in trip_object.get_trip_instructions()
        ]

        # Append to final_tuples list
        final_tuples.extend(instructions_tuples)

    return final_tuples

def insert_data(trip_objects, table, cursor, cnx):
    """
    Inserts data into a specified table in the MySQL db google_maps.

    Parameters
    ----------
    trip_object: List of 2 Directions trip objects containing information
                 to be inserted into the MySQL table. First object contains
                 info from my house to gf and second object is the other trip.
    table: [str] Specifies which table in google_maps to add to.
    cnx: connection object from mysql.connector.
    cursor: cursor of cnx object.
    """

    if table == 'trips':
        data_tuples = create_trips_tuples(trip_objects)
        insert_statement = insert_statement = """
            INSERT INTO
              google_maps.trips (departure_time, trip_direction, trip_duration)
            VALUES
              (%s, %s, %s);
        """

    elif table == 'instructions':
        data_tuples = create_instructions_tuples(trip_objects)
        insert_statement = """
            INSERT INTO
              google_maps.instructions (
                departure_time, trip_direction,
                trip_step, transit_line, step_duration
              )
            VALUES
              (%s, %s, %s, %s, %s);
        """

    cursor.executemany(insert_statement, data_tuples)
    cnx.commit()

def load_directions(trip_objects):
    """
    Loads trip object data into MySQL RDS db named google_maps. Opens and closes
    connection to MySQL db to avoid lingering connections.

    Parameters
    ----------
    trip_objects: list of two Directions objects corresponding to the trips
        between two locations. This can be gotten from the output of
        extract_transform_directions().
    """
    # Connect to MySQL db
    cnx, cursor = helpers.open_connection()

    # Insert trip and instructions data into MySQL db
    for table in ['trips', 'instructions']:
        insert_data(trip_objects, table, cursor, cnx)

    # Close connection to MySQL db
    helpers.close_connection(cnx, cursor)


### FULL ETL ###


def etl():
    """
    Wraps together all ETL.
    """
    # Extract/Transform
    trip_objects = extract_transform_directions(
        config.my_address, config.gf_address, config.api_key
    )
    # Load
    load_directions(trip_objects)

### SCRIPT FOR NOW ###

if __name__ == '__main__':
    etl()
