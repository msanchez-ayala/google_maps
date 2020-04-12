"""
This module contains queries for all PostgreSQL table operations, including
DROP, CREATE, and INSERT statements. This module is used heavily in both
create_table.py and etl.py.

Author: M. Sanchez-Ayala (04/11/2020)
"""

### DROP TABLES ###

locations_table_drop = "DROP TABLE IF EXISTS locations"
time_table_drop = "DROP TABLE IF EXISTS time"
trips_table_drop = "DROP TABLE IF EXISTS trips"
steps_table_drop = "DROP TABLE IF EXISTS steps"

### CREATE TABLES ###

locations_table_create = """
    CREATE TABLE IF NOT EXISTS
      locations (
        location_id CHAR(1) PRIMARY KEY,
        latitude NUMERIC NOT NULL,
        longitude NUMERIC NOT NULL
      )
"""

trips_table_create = """
    CREATE TABLE IF NOT EXISTS
      trips (
        trip_id SERIAL PRIMARY KEY,
        starting_loc_id CHAR(1) NOT NULL REFERENCES locations(location_id),
        duration INT NOT NULL,
        num_steps SMALLINT NOT NULL
      )
"""

time_table_create = """
    CREATE TABLE IF NOT EXISTS
      time (
        trip_id INT PRIMARY KEY REFERENCES trips(trip_id),
        departure_time TIMESTAMP NOT NULL,
        minute INT,
        hour INT,
        day INT,
        week_of_year INT,
        month INT,
        year INT,
        is_weekday BOOLEAN
      )
"""

steps_table_create = """
    CREATE TABLE IF NOT EXISTS
      steps (
        trip_id INT REFERENCES trips(trip_id),
        step_num SMALLINT,
        line_name VARCHAR(5)
      )
"""

### INSERT TABLES ###

locations_table_insert = """
    INSERT INTO TABLE
      locations (
        location_id,
        latitude,
        longitude
      )
    VALUES
      (%s, %s, %s)
    ON CONFLICT DO NOTHING
"""

trips_table_insert = """
    INSERT INTO TABLE
      trips (
        trip_id,
        starting_loc_id,
        duration,
        num_steps
      )
    VALUES
      (DEFAULT, %s, %s, %s)
"""

time_table_insert = """
    INSERT INTO TABLE
      time (
        trip_id,
        departure_time,
        minute,
        hour,
        day,
        week_of_year,
        month,
        year,
        is_weekday
      )
    VALUES
      (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

steps_table_insert = """
    INSERT INTO TABLE
      steps (
        trip_id,
        step_num,
        line_name
      )
    VALUES
      (%s, %s, %s)
"""

### QUERY LISTS ###

drop_table_queries = [
    locations_table_drop,
    trips_table_drop,
    time_table_drop,
    steps_table_drop
]
create_table_queries = [
    locations_table_drop,
    trips_table_drop,
    time_table_drop,
    steps_table_drop
]

insert_table_queries = [
    locations_table_insert,
    trips_table_insert,
    time_table_insert,
    steps_table_insert
]
