"""
This module calls the Google Maps API, parses information, and stores into
google_maps.trips MySQL db.
"""
from datetime import datetime
import os
import json
import glob
import psycopg2
import time
from sql_queries import *


def extract_json(filepath):
    """
    Returns
    -------
    json_file: [dict] The JSON file in usable format

    Parameters
    ----------
    filepath: [str] The filepath to this particular JSON file
    """
    with open(filepath, 'r') as f:
        json_file = json.load(f)

    return json_file


def transform_time(data):
    """
    Returns
    -------
    Tuple of values to be inserted into time table

    Parameters
    ----------
    data: a dictionary representing the parsed JSON data file with trip info.
    """
    date = datetime.fromtimestamp(data['departure_time'])

    departure_timestamp = data['departure_time']
    minute = date.minute
    hour = date.hour
    day = date.isoweekday()
    week_of_year = date.isocalendar()[1]
    month = date.month
    year = date.year

    if day in [6, 7]:
        is_weekday = False
    else:
        is_weekday = True

    return (
        departure_timestamp,
        minute,
        hour,
        day,
        week_of_year,
        month,
        year,
        is_weekday
    )


def transform_location(data):
    """
    Returns
    -------
    Tuple of values to be inserted into locations table.

    Parameters
    ----------
    data: a dictionary representing the parsed JSON data file with trip info.
    """
    return (
        data['start_location_id'],
        data['start_location']['lat'],
        data['start_location']['lng']
    )


def transform_trip(data):
    """
    Returns
    -------
    Tuple of values to be inserted into trips table

    Parameters
    ----------
    data: a dictionary representing the parsed JSON data file with trip info.
    """
    return (
        data['departure_time'],
        data['start_location_id'],
        data['duration'],
        len(data['steps'])
    )


def transform_steps(data):
    """
    Returns
    -------
    Tuple of values to be inserted into steps table

    Parameters
    ----------
    data: a dictionary representing the parsed JSON data file with trip info.
    """
    steps = data['steps']

    return [
        (
            data['departure_time'],
            data['start_location_id'],
            step['step'],
            step['line_name']
        )
        for step in steps
    ]


def load_data(filepath, cur):
    """
    Loads `data` into all four tables in postgres.

    Parameters
    ----------
    filepath: [str] The filepath to the JSON file to load.

    cur: cursor
    """
    data = extract_json(filepath)

    trips_data = transform_trip(data)
    location_data = transform_location(data)
    time_data = transform_time(data)
    steps_data = transform_steps(data)

    cur.execute(trips_table_insert, trips_data)
    cur.execute(locations_table_insert, location_data)
    cur.execute(time_table_insert, time_data)
    for step in steps_data:
        cur.execute(steps_table_insert, step)


def process_data(cur, conn, filepath):
    """
    Bundles up ETL for all data.

    Parameters
    ----------
    cur, conn: cursor and connection to the google_maps postgres database.

    filepath: string containing the filepath to the data directory.

    func: function that performs ETL on the given set of files.
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and perform ETL
    for i, datafile in enumerate(all_files, 1):
        try:
            load_data(datafile, cur)
            # Only display progress every 50 files
            if (not i % 50) or (i == num_files):
                print('{}/{} files processed.'.format(i, num_files))
        except json.decoder.JSONDecodeError as e:
            print(e)
            print(datafile)


def main():
    """
    Connects to google_maps db, performs ETL on directions JSON files and then
    closes the connection to the database.
    """
    conn = psycopg2.connect(
        host = '127.0.0.1',
        dbname = 'google_maps',
        user = 'google_user',
        password = 'passw0rd',
    )
    conn.set_session(autocommit = True)
    cur = conn.cursor()

    process_data(cur, conn, filepath='data')

    conn.close()


if __name__ == '__main__':
    main()
