"""
This module calls the Google Maps API, parses information, and stores into
google_maps.trips MySQL db.

"""
import config
import googlemaps
from datetime import datetime
from Directions import Directions
import mysql.connector
import helpers

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

def open_connection():
    """
    Returns
    -------
    Connection and cursor objects representing a connection to the db.
    """
    cnx = mysql.connector.connect(
        host = config.host,
        user = config.user,
        passwd = config.password
    )
    cursor = cnx.cursor()
    return cnx, cursor

def close_connection(cnx, cursor):
    """
    Closes connection to the db.

    Parameters
    ----------
    cnx: connection object from mysql.connector.
    cursor: cursor of cnx object.
    """
    cnx.close()
    cursor.close()

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
    cnx, cursor = open_connection()

    # Insert trip and instructions data into MySQL db
    for table in ['trips', 'instructions']:
        helpers.insert_data(trip_objects, table, cursor, cnx)

    # Close connection to MySQL db
    close_connection(cnx, cursor)

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

if __name__ == '__main__':
    etl()
