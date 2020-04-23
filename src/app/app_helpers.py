"""
Helper functions for app.py. Includes postgres database connection,
querying the db, pandas data manipulation, and generation of Plotly figs for
Dash.

Author: M. Sanchez-Ayala (04/14/2020)
"""

import psycopg2
import pandas as pd
from pandas.io.sql import read_sql_query
import plotly.graph_objects as go
from consts import *
from sql_queries import trips_time_select


### ALL-PURPOSE PROCESSING ###


def open_connection():
    """
    Returns
    -------
    psycopg2 connection object to google_maps db.
    """
    conn = psycopg2.connect(
        host = '127.0.0.1',
        dbname = 'google_maps',
        user = 'google_user',
        password = 'passw0rd',
    )

    return conn


def create_df():
    """
    Returns
    -------
    tod_df: [Pandas df] of the query inner joining trips and time tables.

    Also closes connection to db.
    """

    query = trips_time_select

    # Connect to db
    conn = open_connection()

    # generate time of day df
    tod_df = read_sql_query(query, conn)

    # Don't want connection to linger
    conn.close()

    return tod_df

def convert_to_day(num):
    """
    Helper for process_df()

    Returns
    -------
    [str] A day of week decoded from the given number.

    Parameters
    ----------
    num: [int] A number from 1 - 7 with 1 being Monday and 7 being Sunday.
    """
    if num == 1:
        return 'Mon'
    elif num == 2:
        return 'Tue'
    elif num == 3:
        return 'Wed'
    elif num == 4:
        return 'Thu'
    elif num == 5:
        return 'Fri'
    elif num == 6:
        return 'Sat'
    elif num == 7:
        return 'Sun'


def process_df(df):
    """
    Returns
    -------
    pro_df: [Pandas Dataframe] A processed copy of the supplied dataframe with some
    modifications necessary for visualization.

    Parameters
    ----------
    df: [Pandas Dataframe] Direct result of SQL query.
    """
    # Copy df
    pro_df = df.copy()

    # Convert ts to datetime
    pro_df['departure_ts'] = pro_df['departure_ts'].map(lambda ts: pd.to_datetime(ts, unit = 's'))

    # Set index and sort
    pro_df.set_index('departure_ts', inplace = True)
    pro_df.sort_values(by = 'departure_ts', inplace = True)

    # Decode the numerical day column to english
    pro_df['day'] = pro_df['day'].map(lambda num: convert_to_day(num))

    return pro_df


def split_df(df):
    """
    Returns
    -------
    List of two dataframes. The inputted df is split based on start_location_id
    for easier Plotly graphing.

    Parameters
    ----------
    df: [Pandas dataframe] time_series dataframe with both start_location_ids. Assumes
    the index is already set to departure_ts.
    """
    df_a = df[df['start_location_id'] == 'A']
    df_b = df[df['start_location_id'] == 'B']

    return [df_a, df_b]


### TIME SERIES UTILS ###


def plot_time_series(dfs, subset = None):
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

    # Add one trace for the data in each df
    for i, df in enumerate(dfs):

        fig.add_trace(go.Scatter(
            x = df.index,
            y = df.duration,
            line_color = graph_colors[i],
            name = df['start_location_id'].values[0] # Legend labels for this trace

        ))

    fig.update_layout(
        title = f'Trip Duration for {subset}' if subset else 'Trip Durations',
        yaxis_title = 'Duration (minutes)',
        xaxis_title = 'Departure Time',
        legend_title = 'Starting Location',
        title_x = title_x_pos,
        title_xanchor = title_x_anchor,
        template = 'plotly_white'
    )

    # fig.show()
    return fig

def time_series_main(df):
    """
    Plots time series from raw dataframe from SQL
    """
    pro_df = process_df(df)

    plot_dfs = split_df(pro_df)

    fig = plot_time_series(plot_dfs)

    return fig


### DESCRIPTIVE STATISTICS UTILS ###


def agg_column(df, column, stats):
    """
    Returns
    -------
    [Pandas df] The original df aggregated and sorted with reset index.

    Parameters
    ----------
    df: [Pandas df] A processed df. Should be output of process_df()

    column: [str] Name of column to group by after location id

    stats: [str, list] Name of statistic(s) to compute.
    """
    if type(stats) == list:
        sort_cols = 'start_location_id'
    elif type(stats) == str:
        sort_cols = ['start_location_id','duration']

    df = df.groupby(['start_location_id',column])
    return df.agg(stats).reset_index().sort_values(sort_cols)


def plot_stats(dfs, column, stats):
    """
    Returns
    -------
    Plotly graph objects fig with bar chart of given column and statistic
    """
    # Instantiate plotly figure
    fig = go.Figure()

    # Add one trace for the data in each df
    for i, df in enumerate(dfs):

        fig.add_trace(go.Bar(
            x = df[column],
            y = df.duration.astype(int),
            marker_color = graph_colors[i],
            name = df['start_location_id'].values[0] # Legend labels for this trace
        ))

    fig.update_layout(
        title = f'{stats.title()} Trip Duration by {column.title()}',
        yaxis_title = 'Duration (minutes)',
        xaxis_title = column.title(),
        title_x = title_x_pos,
        title_xanchor = title_x_anchor,
        legend_title = 'Starting Location',
        template = 'plotly_white'
    )

    return fig


def stats_main(df, stats):
    """
    Returns
    -------
    Dict of plotly graph objects figures for each breakdown plot for the given
    data and statistic to display.

    Parameters
    ----------
    df: [Pandas df] raw dataframe from SQL query

    stats: [str] statistic to display
    """
    pro_df = process_df(df)

    figs = {}
    for column in ['hour', 'day', 'is_weekday']:
        stats_df = agg_column(pro_df, column, stats)
        stats_dfs = split_df(stats_df)
        fig = plot_stats(stats_dfs, column, stats)
        figs[column] = fig

    return figs
