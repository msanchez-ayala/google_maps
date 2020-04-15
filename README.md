# Travel Time Optimization with Google Maps

My girlfriend and I live in two different NYC boroughs, making travel between our
apartments a real pain.
Although Uber/Lyft are not too expensive at off-peak times, my method of choice
is public transit since I already have a
monthly unlimited pass.

It usually takes around an hour to get between our apartments, given that I
typically only make the trip on the weekends.
I started this project to figure out when we can get between our apartments the
quickest via public transportation, namely subway and bus.

## Data and Outcomes

The objective is to collect the "best trip" information from the Google Maps API
every 5 minutes for one week from 1) my apartment to my girlfriend's and 2) her
apartment to mine. The workflow is as follows:

**data_collection.py:** A module configured with cron to run on a Google Compute
Engine VM every 5 minutes for a week.
This module calls the Google Maps API for public transit directions between the
two locations.
Each individual trip is saved as a JSON file in a public Google Cloud Storage
bucket. E.g.
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
**app.sh:** A bash script that wraps together the remaining modules and processes.
It starts a PostgreSQL Docker container and then does the following:
  1. Activates python virtual environment and install dependencies.
  2. Runs **download_storage.py**, which downloads all contents of the GCS bucket locally (~10 MB). This step can be slow (maybe a couple mintues) because GCS does not
  allow for batch downloads. We unfortunately have to pull each JSON individually.
  2. Runs **create_tables.py**, which connects to the Docker container and creates the database and all tables we'll need to populate.
  3. Runs **etl.py**, which populates the database by extracting/transforming the data downloaded by **download_storage.py**.
  4. Runs **app.py**, which is a Dash app to visualize some simple queries on data in our database.

## App

![gif1](/images/gif1.gif)
![gif2](/images/gif2.gif)

## Database Schema

![erd](/images/erd.jpeg)

We have one fact table, `trips`, and three dimension tables, `steps`, `locations`,
and `time`.
Joining `trips` and `time` can answer most simple questions we have such as what
times of day will be quickest for travel. However, we still have other tables such as
`steps` that could tell us some stats about perhaps which train/bus lines are most
common in each route. We can also find the times of day that will require fewest transfers.

## How-To: Access my data and visualize in Dash

Any machine can access my Google Cloud Storage Bucket and run the app. You will
need to complete 3 things prior to running the app.
1. Clone the directory
2. Pull the Docker image
3. Set up python3 venv

Clone this repo and change directories to the new `google_maps` directory in your terminal.
```
git clone https://github.com/msanchez-ayala/google_maps.git
```
Navigate to the new directory
```
cd google_maps
```
Log into Docker (if not already)
```
docker login
```
Pull my Docker image containing PostgreSQL
```
docker pull msanchezayala/google-maps
```
Set up a virtual environment in `google_maps`
```
python3 -m venv ./
```
Lastly, run the bash script that will take care of the rest (see description above)
```
bash app.sh
```

## Challenges

I struggled figuring out how to design the database schema. Most of my
tables operate on compound primary keys. I would love to eliminate that, but
I am generating all of the data myself. I suppose it wouldn't be too
difficult to assign some unique keys within **data_collection.py**.

This was my first time setting up an end-to-end app like this that can be
shared with other users. In fact, it was my first time ever using tools
like Compute Engine and Storage. The hardest part of this project was just
figuring out how to orchestrate and harmonize all of the processes.

That being said, I a lot of fun learning everything and know that this
experience will help greatly speed up any subsequent projects I develop
that involve the same or similar tools. As an old music teacher of mine
used to say, "this will never be as difficult or painful as it the first
time you do it."



## Next Steps

This project has huge potential. I've limited the scope severely so as to not
take up too much time for now. Some low-hanging fruit for expansion:

- Expand to other modes of transportation (driving, walking, biking)
- Try other locations. For instance, it could be used to find the optimal
commute time.
- There are some machine learning applications too such as combining more
data sets such as weather and seeing how that affects ride times.
