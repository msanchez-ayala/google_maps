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

trips_table_create = """
    CREATE TABLE IF NOT EXISTS
      trips (
        trip_id SERIAL PRIMARY KEY,
        departure_ts BIGINT NOT NULL,
        start_location_id CHAR(1) NOT NULL,
        duration INT NOT NULL,
        num_steps SMALLINT NOT NULL
      )
"""

locations_table_create = """
    CREATE TABLE IF NOT EXISTS
      locations (
        location_id CHAR(1) PRIMARY KEY,
        latitude NUMERIC NOT NULL,
        longitude NUMERIC NOT NULL
      )
"""

time_table_create = """
    CREATE TABLE IF NOT EXISTS
      time (
        departure_ts BIGINT NOT NULL,
        minute INT,
        hour INT,
        day INT,
        week_of_year INT,
        month INT,
        year INT,
        is_weekday BOOLEAN,
        PRIMARY KEY(departure_ts)
      )
"""

steps_table_create = """
    CREATE TABLE IF NOT EXISTS
      steps (
        departure_ts BIGINT NOT NULL,
        start_location_id CHAR(1) NOT NULL,
        step_num SMALLINT,
        line_name VARCHAR(5),
        PRIMARY KEY(departure_ts, start_location_id, step_num)
      )
"""

### INSERT TABLES ###

trips_table_insert = """
    INSERT INTO
      trips (
        trip_id,
        departure_ts,
        start_location_id,
        duration,
        num_steps
      )
    VALUES
      (DEFAULT, %s, %s, %s, %s)
"""

locations_table_insert = """
    INSERT INTO
      locations (
        location_id,
        latitude,
        longitude
      )
    VALUES
      (%s, %s, %s)
    ON CONFLICT DO NOTHING
"""

time_table_insert = """
    INSERT INTO
      time (
        departure_ts,
        minute,
        hour,
        day,
        week_of_year,
        month,
        year,
        is_weekday
      )
    VALUES
      (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING
"""

steps_table_insert = """
    INSERT INTO
      steps (
        departure_ts,
        start_location_id,
        step_num,
        line_name
      )
    VALUES
      (%s, %s, %s, %s)
"""

### QUERIES FOR APP ###

trips_time_create = """
    CREATE OR REPLACE VIEW
      trips_time
    AS
    SELECT
      *
    FROM
      trips
    JOIN
      time
    USING
      (departure_ts)
"""

### QUERY LISTS ###

drop_table_queries = [
    trips_table_drop,
    locations_table_drop,
    time_table_drop,
    steps_table_drop
]

create_table_queries = [
    time_table_create,
    locations_table_create,
    trips_table_create,
    steps_table_create
]

insert_table_queries = [
    time_table_insert,
    locations_table_insert,
    trips_table_insert,
    steps_table_insert
]
