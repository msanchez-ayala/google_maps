import pandas as pd
import plotly.graph_objects as go
import mysql.connector 
import config


"""
MySQL HELPERS
-------------
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
DATA MANIPULATION HELPERS
-------------------------
"""    

def get_dfs(kind):
    """
    RETURNS
    -------
    A list of two dataframes for trips data. One for trips to gf and another for trips to me.
    
    PARAMETERS
    ----------
    kind: [str] either trips or instructions. Determines what SQL query is made
    """
    assert kind in ['trips', 'instructions'], 'Invalid type of dataframe'
    
    # Establish connection to MySQL db and connect to db `google_maps`
    cnx = mysql.connector.connect(
        host = config.host,
        user = config.user,
        passwd = config.password
    )
    cursor = cnx.cursor()
    cursor.execute("USE google_maps")
    
    
    # Get all data after 2/18 and store as a df
    cursor.execute(f"""SELECT * FROM {kind} WHERE DAY(departure_time) > 18;""")
    trip_df = pd.DataFrame(cursor.fetchall())
    
    # Retrieve column names
    trip_df.columns = [x[0] for x in cursor.description]
    
    cnx.close()
    cursor.close()
    
    # Call helper to create engineered features and return list of 2 dfs
    return create_features(trip_df)
    
    
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
    return [df_to_gf, df_to_me]

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


"""
PLOTTING FUNCTIONS AND HELPERS
-------------------------------
"""


def assert_subset(subset):
    """
    Helper for plotting functions below. Asserts that subset is in the allowed subsets.
    """
    allowed_subsets = ['All Trips', 'Weekdays', 'Weekends', 'Morning', 
                       'Afternoon', 'Evening', 'Early Morning']
    
    assert subset in allowed_subsets, 'Please select an allowed subset from the documentation.'
    

def plot_boxes(dfs, subset = None):
    """
    RETURNS
    -------
    A figure comparing box plots of trip duration for the two DataFrames passed as arguments.
    
    PARAMETERS
    ----------
    dfs: [list] two DataFrames, one being the trip to gf slice and the other being trip to me slice.
         These dfs must already have all of the engineered features from create_features().
         
    subset: [str] Denotes the subset these dfs belong to. Can be one of:
            ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon', Evening', 'Early Morning']
    """        
    if subset:
        assert_subset(subset)
    
    # Instantiate plotly figure
    fig = go.Figure()

    # Add a single trace for the data in each df
    for df in dfs:
        
        fig.add_trace(go.Box(
            y = df.trip_duration,                    # y values for this trace
            name = df.trip_direction_text.values[0], # x label for this trace
        ))

    fig.update_layout(
        title = f'Transit Trip Duration for {subset}' if subset else 'Transit Trip Duration',
        yaxis_title = 'Minutes',
        template = 'plotly_white',
        showlegend = False
    )

    fig.show()
    
def plot_trip_ts(dfs, subset = None):
    """
    RETURNS
    -------
    A time series of trip durations for the two DataFrames passed as arguments.
    
    PARAMETERS
    ----------
    dfs: [list] two DataFrames, one being the trip to gf slice and the other being trip to me slice.
         These dfs must already have all of the engineered features from create_features().
         
    subset: [str] Denotes the subset these dfs belong to. Can be one of:
            ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon', Evening', 'Early Morning']
    """
    if subset:
        assert_subset(subset)
        
    # Instantiate plotly figure    
    fig = go.Figure()

    # Add a single trace for the data in each df
    for df in dfs:

        fig.add_trace(go.Scatter(
            x = df.departure_time,                       
            y = df.trip_duration,
            name = df['trip_direction_text'].values[0], # Legend labels for this trace
        ))
    
    fig.update_layout(
        title = f'Transit Trip Duration for {subset}' if subset else 'Transit Trip Duration',
        yaxis_title = 'Minutes',
        xaxis_title = 'Departure Time',
        template = 'plotly_white'
    )

    fig.show()

def plot_transfers(dfs, subset = None):
    """
    RETURNS
    -------
    A bar graph comparing number of transfers between trip directions.
    
    PARAMETERS
    ----------
    dfs: [list] two DataFrames, one being the trip to gf slice and the other being trip to me slice.
         These dfs must already have all of the engineered features from create_features().
         
    subset: [str] Denotes the subset these dfs belong to. Can be one of:
            ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon', Evening', 'Early Morning']
    """
    # The no. of steps for each departure time for trips to my gf's apartment. No. of transfers = no. of lines - 1
    instr_to_gf_transfers = dfs[0].groupby(by='departure_time')['trip_direction'].count() - 1

    # The no. of steps for each departure time for trips to my apartment. No. of transfers = no. of lines - 1
    instr_to_me_transfers = dfs[1].groupby(by='departure_time')['trip_direction'].count() - 1

    # Instantiate plotly fig
    fig = go.Figure()

    # Add a single trace for the data in each df
    fig.add_trace(go.Histogram(
        
        x = instr_to_gf_transfers.values,
        name = 'Trips to gf'
        ))

    fig.add_trace(go.Histogram(
        x = instr_to_me_transfers.values,
        name = 'Trips to me'
    ))

    fig.update_layout(
        title = f'Number of Transfers per Trip for {subset}' if subset else 'Number of Transfers per Trip',
        xaxis_title = 'No. of Transfers',
        template = 'plotly_white'
    )
    
    fig.show()
    
def plot_line_freq(df, subset = None):
    """
    RETURNS
    -------
    A bar graph of frequency that a .
    
    PARAMETERS
    ----------
    dfs: [list] two DataFrames, one being the trip to gf slice and the other being trip to me slice.
         These dfs must already have all of the engineered features from create_features().
         
    subset: [str] Denotes the subset these dfs belong to. Can be one of:
            ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon', Evening', 'Early Morning']
    """
    
    # Store trip direction text
    trip_direction = df['trip_direction_text'].values[0]
    
    # Find counts of each transit line for this trip direction. Then sort descending and keep only the first column since
    # they will all tell us the exact same info
    transit_lines = df.groupby(by='transit_line').count().sort_values(by='trip_direction',ascending=False).iloc[:,0]

    # Instantiate figure
    fig = go.Figure()

    # add bars
    fig.add_trace(go.Bar(
        x=transit_lines.index,
        y=transit_lines.values
    ))

    
    fig.update_layout(
        title = f'Transit Line Frequency for {subset}' if subset else 'Transit Line Frequency',
        yaxis_title = 'No. of Times Recommended to Take',
        xaxis_title = 'Transit Line (Subway or Bus)',
        template = 'plotly_white'
    )

    fig.show()
        