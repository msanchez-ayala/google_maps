# Run PostgreSQL Docker container - must go before download so that this
# has time to initialize. Otherwise, download_storage.py will throw an error.
docker run --name google_maps_container -p 5432:5432 -d msanchezayala/google-maps

# # Download data to the data/ subdir (created by this scirpt if not exists)
# python ./src/etl/download_storage.py

# # Create the tables for the database
python ./src/etl/create_tables.py

# Perform ETL
python ./src/etl/etl.py

# Launch Dash app
python ./src/app/app.py
