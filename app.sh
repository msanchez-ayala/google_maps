# Run PostgreSQL Docker container - must go before download so that this
# has time to initialize. Otherwise, download_storage.py will throw an error.
docker run --name google_maps_container -p 5432:5432 -d msanchezayala/google-maps

# Download data to the data subdirectory (created by this scirpt if not exists)
python download_storage.py

# Create the tables for the database
python create_tables.py

# Perform ETL
python etl.py

# Launch Dash app
python app.py
