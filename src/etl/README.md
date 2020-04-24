## My ETL Pipeline
![pipeline](/images/pipeline.jpeg)

1. Call Google Maps API for trip instructions between two locations for both
directions of the trip (JSON) every 5 minutes. This is run on a Google Compute
Engine VM instance.
2. Store each JSON in a Google Cloud Storage bucket acting as a data lake.
3. Pull down all data from the GCS bucket to my local machine.
4. Run a Docker container hosting PostgreSQL.
5. Create and populate a PostgreSQL database using the star schema shown below.


## Implementation

### Data Collection
`data_collection.py:` A module that calls the Google Maps API for public transit
directions between the two locations. Each individual trip is saved as a JSON
file in a public Google Cloud Storage bucket. E.g.
```
{
  "start_location": {"lat": 40.7087015, "lng": -73.9416712},
  "start_location_id": "A",
  "departure_time": 1586809354,
  "arrival_time": 1586812163,
  "duration": 46,
  "steps": [{"step": 1, "distance": 1490, "html_instructions": "Subway towards 8 Av", "line_name": "L"}, {"step": 2, "distance": 4403, "html_instructions": "Subway towards Court Sq - 23 St", "line_name": "G"}, {"step": 3, "distance": 9957, "html_instructions": "Subway towards Jamaica Center - Parsons/Archer", "line_name": "E"}]
}
```
There is the option to save these purely locally though, as discussed in the
instructions of the main README for this project.

In order to schedule this script, I chose to create a cron job that runs the
bash script `data_collection.sh` in this repo's root directory every 5 minutes.
That script sets up the virtual environment, sets a key environment variable,
and executes the data collection.

### Running the app

`app.sh:` A bash script in the root directory of this repo that wraps together
the remaining modules and processes. It starts a PostgreSQL Docker container and
then does the following:
  1. Runs `create_tables.py`, which connects to the Docker container and creates the database and all tables we'll need to populate.
  2. Runs `etl.py`, which populates the database by extracting/transforming the
  data in `google_maps/data/*/*.json`. This takes a minute or two because it
  processes files individually.
  3. Runs `app.py`, which triggers a Dash app to visualize some simple queries
  on data in our database.


## Database Schema

![erd](/images/erd.jpeg)

We have one fact table, `trips`, and three dimension tables, `steps`, `locations`,
and `time`.
Joining `trips` and `time` can answer most simple questions we have such as what
times of day will be quickest for travel. However, we still have other tables such as
`steps` that could tell us some stats about perhaps which train/bus lines are most
common in each route. We can also find the times of day that will require fewest transfers.
