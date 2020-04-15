# Run PostgreSQL Docker container - must go before download so that this
# has time to initialize. Otherwise, download_storage.py will throw an error.
docker run --name google_maps_container -p 5432:5432 -d msanchezayala/google-maps

# Activate venv and install dependencies just in case
source ./bin/activate
pip install -r requirements.txt

# Download data to the data subdirectory (created by this scirpt if not exists)
python download_storage.py

# Create the tables for the database
python create_tables.py

# Perform ETL
python etl.py

# Launch Dash app
python app.py

# Comment these lines out if you want to keep using the container and/or venv
docker stop google_maps_container
docker rm google_maps_container
deactivate
