# Travel Time Optimization

My girlfriend and I live in two different NYC boroughs, making travel between our apartments a real pain.
Although Uber/Lyft are not too expensive at off-peak times, my method of choice is public transit since I already have a
monthly unlimited pass.

It usually takes around an hour to get between our apartments, given that I typically only make the trip on the weekends.
I started this project to figure out when we can get between our apartments the quickest via public transportation,
namely subway and bus.

## Data and Outcomes

The objective is to collect the "best trip" information from the Google Maps API
every 5 minutes for one week from 1) my apartment to my girlfriend's and 2) her
apartment to mine. The workflow is as follows:
- **data_collection.py:** configured with cron to run on a Google Compute Engine
VM every 5 minutes for a week. This module calls the Google Maps API for public
transit directions between the two locations.
  - Each individual trip is saved as a JSON file that gets pushed to a public
  GCS bucket.
- A Docker container hosting a PostgreSQL database can be run locally at any
time to monitor the incoming data by running the following scripts:
  1. **download_storage.py**: Downloads all contents of the GCS bucket locally.
  2. **create_tables.py** Connects to the PostgreSQL container and creates the db.
  3. **etl.py:** Populates the db.
  4. **app.py:** Runs the Dash app, which is a Flask app that displays a dashboard
  of analytical queries for this project.

## How-to

Any machine ca access my Google Cloud Storage Bucket and run the app. You will
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
docker login.io
```
Pull my Docker image containing PostgreSQL
```
docker pull msanchezayala/google-maps
```
Set up a virtual environment in `google_maps`
```
python3 -m venv ./
```
Activate it and install dependencies
```
source ./bin/activate

pip install -r requirements.txt
```
Lastly, run the bash script that will take care of the rest (run the container and execute python files in correct order)
```
bash app.sh
```
