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


    Instance Variables (All immutable)
    ----------------------------------
    trip_start: [datetime] datetime object of when the API call was made.
    trip_duration: [int] total duration of the trip in minutes.
    trip_instructions: [dict] with train/bus lines and time on each one.
    """

    def __init__(self, start_coords, end_coords, mode, gmaps):
        self._gmaps = gmaps
        self._trip_start = datetime.now()
        self._directions = self._extract_directions(
            start_coords, end_coords, mode
        )
        self._trip_duration = self._transform_times()
        # self._trip_instructions = self._transform_directions()


    def _extract_directions(self, start_coords, end_coords, mode):
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


    def _to_datetime(self, which_time):
        """
        Returns
        -------
        Arrival or departure time from the current instance of this object
        as a datetime object in %H:%M%p.

        Parameters
        ----------
        which_time: [str] Either 'arrival_time' or 'departure_time'
        """
        time = self._directions[0]['legs'][0][which_time]['text']
        dtime = datetime.strptime(time, '%H:%M%p')
        return dtime

    def _replace_hour(self, arrival_datetime, departure_datetime):
        """
        Returns
        -------
        arrival_datetime with the hour potentially reset depending on the time
        difference between two inputted times.

        Parameters
        ----------
        arrival_datetime: [datetime] Arrival time to destination in the instance
            of this trip.
        departure_datetime: [datetime] Departure time to destination in the
            instance of this trip.
        """
        # The logic is that when we go from 12 am/pm -> 1am/pm, we don't want the
        # timedelta object to show an hour difference of 11 hours. Thus, account
        # for when departure hr > arrival hr.
        if departure_datetime.hour > arrival_datetime.hour:
            departure_datetime = departure_datetime.replace(hour=0)
        return departure_datetime

    def _transform_times(self):
        """
        Returns
        -------
        Trip duration in minutes as an int.
        """
        # Convert arrival and departure times to datetime
        arrival_datetime = self._to_datetime('arrival_time')
        departure_datetime = self._to_datetime('departure_time')

        # Replace the departure_datetime hour depending on arrival_time
        departure_datetime = self._replace_hour(
            arrival_datetime, departure_datetime
        )

        # Calculate timedelta, convert to minutes
        trip_duration = int((arrival_datetime - departure_datetime).seconds/60)

        return trip_duration

    def get_trip_duration(self):
        """
        Getter method for trip_duration in minutes as int
        """
        return self._trip_duration

    # def _transform_directions():

    def get_trip_instructions(self):
        """
        Returns
        -------
        A dictionary with which trains/buses to take in this trip and how long each one will take.

        Parameters
        ----------

        directions: [JSON] raw directions contained within self._directions
        """
        # Empty container for results
        directions_list = []

        # Isolate just the specific trip directions
        directions = self._directions[0]['legs'][0]['steps']

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
