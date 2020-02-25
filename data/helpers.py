import pandas as pd

"""
HELPER FUNCTIONS FOR MySQL
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
    
    
"""
HELPER FUNCTIONS FOR DATA MANIPULATION
"""    
    
    
def assign_trip_direction_text(value):
    """
    Helper for create_features()
    
    RETURNS
    -------
    Text decoding the trip direction names. 
    
    PARAMETERS
    ----------
    value: [int] either 0 or 1
    """
    
    if value == 0:
        return 'Trip to gf'
    elif value == 1:
        return 'Trip to me'
    
def assign_time_of_day(timestamp):
    """
    Helper for create_features()
    
    RETURNS
    -------
    The time of day it is based off of departure_time timestamp.
    
    PARAMETERS
    ----------
    timestamp: [timestamp] object of the departure_time for a given trip
    
    TIME CUTOFFS
    ------------
    early_morning = 0:00
    morning       = 5:00
    afternoon     = 12:00
    evening       = 17:00
    """   
    hour = timestamp.hour
    if (hour >= 0) and (hour < 5):
        return 'Early morning'
    elif (hour >= 5) and (hour < 12):
        return 'Morning'
    elif (hour >= 12) and (hour < 17):
        return 'Afternoon'
    elif hour >= 17:
        return 'Evening'

def assign_weekday(day_of_week):
    """
    Helper for create_features()
    
    RETURNS
    -------
    0 if the day of week is a weekend day 
    1 if weekday
    
    PARAMETERS
    ----------
    day_of_week: [int] day of week from 0 (Mon) to 6(Sun)
    """
    if day_of_week in [5,6]:
        return 0
    else:
        return 1
    
def create_features(df):
    """
    Function wrapping up helpers above into a small pipeline to clean some data
    and assign new features that will be helpful in our investigation.
    
    RETURNS
    -------
    A DataFrame with newly engineered features and a list of the two dataframes 
    grouped by trip direction.
    
    
    PARAMETERS
    ----------
    df: [DataFrame] Containing unmodified data straight from SQL.
    
    """
    # Convert all date strings to datetime
    df['departure_time'] = pd.to_datetime(df['departure_time'])

    # Assign time of day
    df['time_of_day'] = df['departure_time'].map(lambda x: assign_time_of_day(x))

    # Assign day of week
    df['day_of_week'] = df['departure_time'].map(lambda x: x.dayofweek)

    # Assign weekday
    df['weekday'] = df['day_of_week'].map(lambda x: assign_weekday(x))

    # Decode trip direction
    df['trip_direction_text'] = df['trip_direction'].map(lambda x: assign_trip_direction_text(x))

    # Group data by trip direction
    df_to_gf = df[df['trip_direction'] == 0]
    df_to_me = df[df['trip_direction'] == 1]

    # Return the modified df and the list of two grouped dfs
    return df, [df_to_gf, df_to_me]

def create_time_of_day_dfs(df):
    """
    RETURNS
    -------
    List of 4 dataframes, each one being a different slice of the original df split into the 4 possible times of day.
    
    Returned in the order: morning, afternoon, evening, early morning
    
    PARAMETERS
    ----------
    df: [DataFrame] parent df that will be subset into morning, afternoon, evening, and early morning.  
    """
    times_of_day = ['Morning', 'Afternoon', 'Evening', 'Early Morning']
    
    return [df[df['time_of_day'] == times_of_day[i]] for i in range(len(times_of_day))]

def create_day_of_week_dfs(df):
    """
    RETURNS
    -------
    List of 7 dataframes, each one being a different slice of the original df split into the 7 days of the week.
    
    Returned in the order: Monday, Tues, ... , Sat, Sun
    
    PARAMETERS
    ----------
    df: [DataFrame] parent df that will be subset into days of week.  
    """
    # Days of week are designated from 0-7 in the df
    return [df[df['day_of_week'] == i] for i in range(0,8)]

def create_weekday_end_dfs(df):
    """
    RETURNS
    -------
    List of 2 dataframes, each one being a different slice of the original df split into weekday or weekend.
    
    Returned in the order: Weekday, weekend
    
    PARAMETERS
    ----------
    df: [DataFrame] parent df that will be subset into weekday/end.  
    """
    # Weekday is 1 and weekend is 0 in this column of the df
    return [df[df['weekday'] == i] for i in [1,0]]
    
