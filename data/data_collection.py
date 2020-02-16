"""
This module will run code developed in data_collection.ipynb to call the
Google Maps API, parse information, and store into google_maps.trips MySQL db.

"""
import config
import googlemaps
from datetime import datetime
from GDirections import GDirections
import mysql.connector
import helpers

# Connect to Google Maps API
gmaps = googlemaps.Client(key=config.api_key)

# Geocode my address, store lat/long
geocode_my_result = gmaps.geocode(config.my_address)
my_geometry = geocode_my_result[0]['geometry']['location']

# Geocoding my girlfriend's address, store lat/lon
geocode_gf_result = gmaps.geocode(config.gf_address)
gf_geometry = geocode_gf_result[0]['geometry']['location']

# Instantiate trip to gf's home, my home
transit_to_gf = GDirections(my_geometry, gf_geometry, 'transit', gmaps)
transit_to_me = GDirections(gf_geometry, my_geometry, 'transit', gmaps)

# Store these together in a list
trip_objects = [transit_to_gf, transit_to_me]

# Create connection to mysql
cnx = mysql.connector.connect(
    host = config.host,
    user = config.user,
    passwd = config.password
)
cursor = cnx.cursor()

# Insert trip data into MySQL db
helpers.insert_data(trip_objects, cursor, cnx)

# Close connection to MySQL
cnx.close()
cursor.close()
