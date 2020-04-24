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

The objective of this project is to collect the "best trip" information from the
Google Maps API every 5 minutes for one week from 1) my apartment to my
girlfriend's and 2) her apartment to mine. I have built an ETL pipeline and a
simple dashboard to visualize the results. The pipeline is discussed in the
README within `/src/etl`.


## Dashboard

This app displays some simple queries from the PostgreSQL database to show
different travel times.

![gif1](/images/gif1.gif)

Scrolling down, we can inspect a few descriptive statistics.

![gif2](/images/gif2.gif)


## How-To: Configuration

You can use this project in a number of ways. All will require the following:
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
Activate and install requirements
```
source ./bin/activate
pip install -r requirements.txt
```
Lastly, unzip the data (if you haven't already). This will vary by OS,
but can be a simple as double-clicking on the file.

### 1. Just the Dashboard
To view the Dash app, all you have to do is run Docker container and then the
`app.sh` bash script
```
docker run --name google_maps_container -p 5432:5432 -d msanchezayala/google-maps
```
Run the bash script, which will create the database, populate it, and launch the app
```
bash app.sh
```
Lastly, paste `127.0.0.1:8050` into your browser when the app starts running.

When done with everything, you can close out of the app with `ctrl + C` and then
running the following to close out of the Docker container
```
docker stop google_maps_container
docker rm google_maps_container
```

### 2. Collect Your Own Data
You will need the following:
1. A Google Maps API key, which you can register for [here](https://developers.google.com/maps/documentation/geocoding/get-api-key)
2. Make sure you enable both Directions API and Geolocation API
3. Create `/src/etl/config.py`
In `config.py` assign following variables:

```
### GOOGLE MAPS API CREDENTIALS ###

api_key = 'your key'

### GEOGRAPHIC LOCATIONS ###

location_A = 'first address exactly as you'd enter into Google Maps'
location_B = 'second address exactly as you'd enter into Google Maps'
```
To collect data, you should schedule a cron task at your desired time interval that runs
`data_collection.sh`. Open the file and fill in the missing
filepath in the first line. Mine was
```
*/5 * * * * bash data_collection.sh > ./log.log 2>&1
```
So that I could keep track of any errors.

##### Pushing to GCP Storage Bucket
If you plan to push each record to GCP storage, make sure to obtain [Google
 Authorization](https://cloud.google.com/docs/authentication/getting-started),
 put the authorization JSON file somewhere and then uncomment google authorization line in `data_collection.sh`:
```
### FILL IN ### absolute path to authorization json
# export GOOGLE_APPLICATION_CREDENTIALS='path_to_your_google_auth.json'
```
Uncomment the last line of `main()` in `src/etl/data_collection.py`

Add to `config.py`
```
project = 'your project number' # This is found in your Google developer console
bucket = 'the storage bucket name where you want to save each record'
```
##### Retrieving Records from your GCP Storage Bucket
This section assumes you've set up `config.py` as specified above. You will just
need to add one variable to `config.py` to do this, which is a variable mapping
to the absolute path of the `google_maps` dir.
```
folder = 'absolute path to google_maps'
```
Make sure there's no forward slash at the end of that particular path, as code in
`src/etl/download_storage.py` already includes it.

Lastly,
```
python src/etl/download_storage.py
```
And your download will begin. This is honestly kind of slow since the Python driver
for Google Cloud only allows you to download individual blobs and not copying the
entire bucket or a particular object. If you have `gsutil` set up then I'd
recommend doing some form of the `cp` command to more quickly get your data.


## Further Directions

This project has lots of potential. I've limited the scope severely so as to
so as to produce something in a reasonable amount of time. Here are some ideas
for expansion that I'd like to consider:

- Add to other modes of transportation (driving, walking, biking)
- Try other locations. For instance, it could be used to find the optimal
commute time.
- There are some machine learning applications too such as combining more
data sets such as weather and seeing how that affects ride times.
- Ideally, I would set up a service to run all the ETL in the cloud so that the
user doesn't need to download this docker image and run all the ETL themselves.
This would likely require more financial resources though, so I will hold off
for now.
