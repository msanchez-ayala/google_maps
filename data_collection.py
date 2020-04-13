"""
This module calls the "best trip" data from the Google Maps API between two
locations via public transit. It parses that information and saves to JSON
in two newly created subdirectories.

Author: M. Sanchez-Ayala (04/10/2020)
"""

from datetime import datetime
import json
import os
import googlemaps
from google.cloud import storage
import config


def establish_directories():
    """
    Checks if the necessary data-storing directories exist. If not, creates them
    within the current directory.
    """
    if not os.path.exists('data'):
        os.mkdir('data')
        os.mkdir('data/A')
        os.mkdir('data/B')
    elif (not os.path.exists('data/A')) or (not os.path.exists('data/B')):
        os.mkdir('data/A')
        os.mkdir('data/B')


def locations_to_coords(location_A, location_B, gmaps_client):
    """
    Returns
    -------
    List of two original location addresses as coordinates.

    Parameters
    -----------
    location_A: [str] First address as you would input into Google Maps.
    location_B: [str] Second address as you would input into Google Maps.


    Examples
    --------
    >>> locations_to_coords(
            'One World Trade Center',
            '476 5th Ave, New York, NY 10018'
        )
    [
        {'lat': 40.7127431, 'lng': -74.0133795},
        {'lat': 40.75318230000001, 'lng': -73.9822534}
    ]
    """
    # Convert each location to coordinates and store in list
    coords = [
        gmaps_client.geocode(location)[0]['geometry']['location']
        for location in [location_A, location_B]
    ]
    return coords


def get_full_directions(gmaps_client, coords, mode, start_time):
    """
    Returns
    --------
    A dict with full trip direction information straight from Google Maps
    API.

    Parameters
    ----------
    gmaps_client: the connection to the Google Maps API.

    coords: [list] Two original location addresses as coordinates.

    mode: [str] A method of transportation. Walking, driving, biking, or transit.

    start_time: [datetime] Time at which the API is called to look for the best trip.
    """

    # Call API
    directions = gmaps_client.directions(
        origin = coords[0],
        destination = coords[1],
        mode = mode,
        departure_time = start_time
    )[0]
    return directions


def parse_steps(steps):
    """
    Returns
    -------
    A list of dictionaries with parsed information on transit steps of the
    trip.

    Parameters
    ----------
    steps: A list of dictinoaries with the full information on each
    individual step of the trip.
    """
    step_directions = []
    step_num = 1
    for step in steps:

        # We'll only consider steps that involve bus or train.
        # Entries for walking don't habe key 'transit_details'
        if step.get('transit_details'):
            distance = step['distance']['value'] # Meters
            instrs = step['html_instructions']
            line_name = step['transit_details']['line']['short_name']
            step_directions.append({
                'step': step_num,
                'distance': distance,
                'html_instructions': instrs,
                'line_name': line_name
            })
            step_num += 1

    return step_directions


def parse_directions(full_directions, start_location_id):
    """
    Returns
    -------
    A parsed `full_directions` dictionary.

    Parameters
    ----------
    full_directions: dict with full trip direction information straight from
    Google Maps API.

    start_location_id: [str] Either 'A' or 'B' depending on whether this is
    trip A or B. User defined.
    """
    trip_directions = {}

    # Abbreviate the path
    legs = full_directions['legs'][0]
    start_location = legs['start_location']           # Coordinates
    start_location_id = start_location_id             # Either A or B
    arrival_time = legs['arrival_time']['value']      # Timestamp
    departure_time = legs['departure_time']['value']  # Timestamp
    duration = int(legs['duration']['value']/60)      # Minutes

    # Abbreviate the next path and parse
    steps = legs['steps']
    step_directions = parse_steps(steps)

    trip_directions = {
        'start_location': start_location,
        'start_location_id': start_location_id,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'duration': duration,
        'steps': step_directions
    }

    return trip_directions


def to_json(trip_directions):
    """
    Saves `trip_directions` as JSON in 'data/{sub_dir}' where sub_dir is
    A or B depending on the start_location_id.

    Parameters
    ----------
    trip_directions: the parsed directions dictionary derived from
    parse_directions() method.
    """
    sub_dir = trip_directions['start_location_id']

    # Convert departure time timestamp to string for JSON naming
    date = datetime.fromtimestamp(trip_directions['departure_time'])
    date_str = datetime.strftime(date, '%Y-%m-%d_%H-%M-%S')
    filename = 'data/{}/{}.json'.format(sub_dir, date_str)

    # Export to a JSON
    with open(filename, 'w') as f:
        json.dump(trip_directions, f)

    return filename

def to_google_storage(filename):
    """
    Connects to Google Cloud storage to upload the current file
    """
    client = storage.Client(
        project = '876275184095'
    )

    bucket = client.get_bucket('g-maps')

    blob = bucket.blob(filename)

    with open(filename, "rb") as json_file:
        blob.upload_from_file(json_file)


def main():
    """
    Wraps data collection together.

    Creates the correct in which to store collected data.
    Connects to Google Maps API and gets the coordinates of the two addresses.
    Exports each trip's parsed directions as a JSON in the subdirectories defined
    above.
    """
    establish_directories()

    # Connect to Google Maps API
    gmaps_client = googlemaps.Client(config.api_key)

    # Convert locations to coordinates
    coords = locations_to_coords(config.location_A, config.location_B, gmaps_client)

    # Set start time and trip specifications
    start_time = datetime.now()
    trips = [
        {'start_location_id': 'A', 'coords': coords},
        {'start_location_id': 'B', 'coords': coords[::-1]}
    ]

    for trip in trips:

        # Get full directions for this trip
        full_directions = get_full_directions(
            gmaps_client, trip['coords'], 'transit', start_time
        )

        # Parse directions for this trip
        parsed_directions = parse_directions(
            full_directions, trip['start_location_id']
        )

        # Export locally to JSON in subdirectory and store file name
        filename = to_json(parsed_directions)

        # Push to Google Storage
        to_google_storage(filename)


if __name__ == '__main__':
    main()
