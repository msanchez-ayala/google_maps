"""
This module will run code developed in data_collection.ipynb to call the
Google Maps API, parse information, and store into google_maps.trips MySQL db.

"""
import config
import googlemaps
from datetime import datetime
import Directions
import mysql.connector
import helpers

# Connect to Google Maps API
gmaps = googlemaps.Client(key=config.api_key)

def get_geometry(address):
    """
    Returns
    -------
    Lat/Long of the supplied address.

    Parameters
    ----------
    address: [str] An address as you would enter it into Google Maps.

    Examples
    --------

    >>> get_geometry('One World Trade Center')
    {'lat': 40.7127431, 'lng': -74.0133795}

    >>> get_geometry('476 5th Ave, New York, NY 10018')
    {'lat': 40.75318230000001, 'lng': -73.9822534}
    """
    geocoded_address = gmaps.geocode(address)
    geometry = geocoded_address[0]['geometry']['location']
    return geometry

# Get geometry for two addresses
my_geometry = get_geometry(config.my_address)
gf_geometry = get_geometry(config.gf_address)

# Instantiate trip to gf's home, my home
transit_to_gf = Directions(my_geometry, gf_geometry, 'transit', gmaps)
transit_to_me = Directions(gf_geometry, my_geometry, 'transit', gmaps)

# Store these together in a list
trip_objects = [transit_to_gf, transit_to_me]

# Create connection to mysql
cnx = mysql.connector.connect(
    host = config.host,
    user = config.user,
    passwd = config.password
)
cursor = cnx.cursor()

# Insert trip and instructions data into MySQL db
helpers.insert_trip_data(trip_objects, cursor, cnx)
helpers.insert_instructions_data(trip_objects, cursor, cnx)

# Close connection to MySQL
cnx.close()
cursor.close()
