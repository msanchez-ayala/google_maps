from datetime import datetime
import googlemaps

class Directions:
    """
    A class to keep track of and display to the user only necessary parts of
    the Google maps searches.

    Parameters
    -----------
    start_coords: [dict] Lat/Lng of starting location in the form
        {'lat': lat, 'lng': lng}.
    end_coords: [dict] Lat/Lng of ending location in the form
        {'lat': lat, 'lng': lng}.
    mode: [str] One of "driving", "walking", "bicycling" or "transit".
    gmaps: googlemaps.Client object.


    Instance Variables
    ----------
    trip_start: [datetime] datetime object of when the API call was made.
    trip_duration: [int] total duration of the trip in minutes.
    trip_instructions: [dict] with train/bus lines and time on each one.
    """

    def __init__(self, start_coords, end_coords, mode, gmaps):
        self._gmaps = gmaps
        self._trip_start = datetime.now()
        self._directions_json = self._retrieve_google_directions_json(
            start_coords, end_coords, mode
        )
        self._trip_duration = self._calculate_trip_duration()


    def _retrieve_google_directions_json(self,start_coords, end_coords, mode):
        """
        Extraction of Google Maps API data.

        Returns
        --------
        A json with trip direction information
        """

        # Call API
        directions = self._gmaps.directions(
            origin = start_coords,
            destination = end_coords,
            mode = mode,
            departure_time = self._trip_start
        )
        return directions

    def _calculate_trip_duration(self):
        """
        Calculate and return trip duration in minutes.

        Returns
        -------
        Trip duration in minutes as an int.
        """

        # Store arrival time and convert to datetime
        arrival_time = self._directions_json[0]['legs'][0]['arrival_time']['text']
        arrival_datetime = datetime.strptime(arrival_time, '%H:%M%p')

        # Store arrival time and convert to datetime
        departure_time = self._directions_json[0]['legs'][0]['departure_time']['text']
        departure_datetime = datetime.strptime(departure_time, '%H:%M%p')

        # When we go from 12 am/pm -> 1am/pm, we don't want to say the hr diff
        # is 11 hours. Thus, account for when departure hr > arrival hr
        if departure_datetime.hour > arrival_datetime.hour:
            departure_datetime = departure_datetime.replace(hour=0)

        # Calculate difference in seconds, convert to minutes
        trip_duration = int( (arrival_datetime - departure_datetime).seconds/60 )

        return trip_duration

    def get_trip_duration(self):
        """
        Getter method for trip_duration in minutes as int
        """
        return self._trip_duration

    def get_trip_instructions(self):
        """
        Returns
        -------
        A dictionary with which trains/buses to take in this trip and how long each one will take.

        Parameters
        ----------

        directions: [JSON] raw directions contained within self._directions_json
        """
        # Empty container for results
        directions_list = []

        # Isolate just the specific trip directions
        directions = self._directions_json[0]['legs'][0]['steps']

        # keep track of which step we're in
        step = 1

        for direction in directions:

            # Ignore any walking instructions
            if direction.get('transit_details'):

                # Store name of bus or train line
                travel_mode = direction['transit_details']['line']['short_name']

                # Store time on that bus or train line in minutes as int
                direction_len = int(direction['duration']['text'].split()[0])

                # Append dict to the results container
                directions_list.append({
                    'step':step,
                    'travel_mode' : travel_mode,
                    'length' : direction_len
                })

                # Next step will be 1 higher
                step += 1

        return directions_list

    def get_trip_start(self):
        return self._trip_start.strftime("%Y/%m/%d %H:%M")
