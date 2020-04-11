from datetime import datetime
import json
import googlemaps
import config


class Directions:
    """
    Connects to the Google Maps API to retrieve directions for a transit trip
    between the two given addresses.

    Parameters
    -----------
    location_1: [str] First address as you would input into Google Maps.
    location_2: [str] Second address as you would input into Google Maps.

    Instance Variables (All immutable)
    ----------------------------------
    trip_start: [datetime] datetime object of when the API call was made.
    trip_duration: [int] total duration of the trip in minutes.
    trip_instructions: [dict] with train/bus lines and time on each one.
    """


    def __init__(self, location_1, location_2):

        # Connect to Google Maps API
        self.gmaps = self.gmaps_client(config.api_key)

        # Convert locations to coordinates
        self.coords = self.locations_to_coords(
            location_1, location_2, self.gmaps
        )

        # Get full directions for trips between both locations
        self.full_directions_A = self.get_full_directions(
            self.gmaps, self.coords
        )
        self.full_directions_B = self.get_full_directions(
            self.gmaps, self.coords[::-1]
        )

        # Get parsed directions for trips between both locations
        self.directions_A = self.get_directions(self.full_directions_A)
        self.directions_B = self.get_directions(self.full_directions_B)

    def gmaps_client(self, api_key):
        """
        Returns
        -------
        The gmaps client, given the key in the config file.

        Parameters
        ----------
        api_key: [str] A Google API key.
        """
        return googlemaps.Client(config.api_key)


    def locations_to_coords(self, location_1, location_2, gmaps):
        """
        Returns
        -------
        List of two original location addresses as coordinates.

        Parameters
        -----------
        location_1: [str] First address as you would input into Google Maps.
        location_2: [str] Second address as you would input into Google Maps.


        Examples
        --------
        >>> self.locations_to_coords(
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
            gmaps.geocode(location)[0]['geometry']['location']
            for location in [location_1, location_2]
        ]
        return coords


    def get_full_directions(self, gmaps, coords):
        """
        Returns
        --------
        A dict with full trip direction information straight from Google Maps
        API.

        Parameters
        ----------
        coords: List of two original location addresses as coordinates.
        """

        # Call API
        directions = gmaps.directions(
            origin = coords[0],
            destination = coords[1],
            mode = 'transit',
            departure_time = datetime.now()
        )[0]
        return directions


    def parse_steps(self, steps):
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


    def get_directions(self, full_directions):
        """
        Returns
        -------
        A parsed `full_directions` dictionary.

        Parameters
        ----------
        full_directions: dict with full trip direction information straight from
        Google Maps API.
        """
        trip_directions = {}

        # Abbreviate the path
        legs = full_directions['legs'][0]
        start_location = legs['start_location']          # Coordinates
        end_location = legs['end_location']              # Coordinates
        arrival_time = legs['arrival_time']['value']     # Timestamp
        departure_time = legs['departure_time']['value'] # Timestamp
        duration = int(legs['duration']['value']/60)     # Minutes


        # Abbreviate the next path and parse
        steps = legs['steps']
        step_directions = self.parse_steps(steps)

        trip_directions = {
            'start_location': start_location,
            'end_location': end_location,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'duration': duration,
            'steps': step_directions
        }

        return trip_directions


    def to_json(self, trip_directions, dir_path=''):
        """
        Saves `trip_directions` as JSON in a directory denoted by `dir_path`

        Parameters
        ----------
        trip_directions: the parsed directions dictionary derived from
        get_directions() method.

        dir_path: [str] The directory (or subdirectory) where this file will be
        stored. Should end with a slash, e.g. 'data/'.
        """
        # Convert departure time timestamp to string for JSON naming
        date = datetime.fromtimestamp(trip_directions['departure_time'])
        date_str = datetime.strftime(date, '%Y-%m-%d_%H-%M-%S')

        # Export to a JSON
        with open(f'{dir_path}{date_str}.json', 'w') as f:
            json.dump(trip_directions, f)
