"""
This module calls the "best trip" data from the Google Maps API between two
locations via public transit. It parses that information and saves to JSON
in two newly created subdirectories.

Author: M. Sanchez-Ayala (04/12/2020)
"""

from datetime import datetime
import json
import os
import googlemaps
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


def get_parsed_directions(full_directions, start_location_id):
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
    get_parsed_directions() method.
    """
    sub_dir = trip_directions['start_location_id']

    # Convert departure time timestamp to string for JSON naming
    date = datetime.fromtimestamp(trip_directions['departure_time'])
    date_str = datetime.strftime(date, '%Y-%m-%d_%H-%M-%S')

    # Export to a JSON
    with open(f'data/{sub_dir}/{date_str}.json', 'w') as f:
        json.dump(trip_directions, f)


def main():
    """
    Wraps data collection together.

    Creates the correct in which to store collected data.
    Connects to Google Maps API and gets the coordinates of the two addresses
    and saves each trip direction as a JSON in the subdirectories defined
    above.
    """
    establish_directories()

    # Connect to Google Maps API
    gmaps_client = googlemaps.Client(config.api_key)

    # Convert locations to coordinates
    coords = locations_to_coords(config.location_A, config.location_B, gmaps_client)

    start_time = datetime.now()

    # Get full directions for trips between both locations
    full_directions_A = get_full_directions(gmaps_client, coords, 'transit', start_time)
    full_directions_B = get_full_directions(gmaps_client, coords[::-1], 'transit', start_time)

    # Parse the directions
    parsed_directions_A = get_parsed_directions(full_directions_A, 'A')
    parsed_directions_B = get_parsed_directions(full_directions_B, 'B')

    # Save parsed directions to JSON files
    directions.to_json(directions.directions_A)
    directions.to_json(directions.directions_B)


if __name__ == '__main__':
    main()