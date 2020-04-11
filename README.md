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
- I call the Google Maps API for public transit directions between the two locations every 5 minutes using Airflow.
- I store each individual trip locally as a JSON file.
- After a week, I run an ETL script to push the information from the JSON files to a PostgreSQL Docker container.
- I then create a simple dashboard using Dash to view sample queries from the database.
- From there, the data can be easily queried and explored with some sample queries in a simple dashboard.

## How-To

1. Create a Python 3.7.4 virtual environment and install the packages in **requirements.txt**.
2.


## TO-DO

1. Set up Airflow
2. Write **etl.py**, **create_tables.py**, and **sql_queries.py**.
  - Maybe separate out the data collection code from ETL code.
3. Build dashboard
