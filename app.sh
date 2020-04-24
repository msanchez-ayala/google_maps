# # Download data to the data/ subdir (created by this scirpt if not exists)
# python ./src/etl/download_storage.py

# # Create the tables for the database
python ./src/etl/create_tables.py

# Perform ETL
python ./src/etl/etl.py

# Launch Dash app
python ./src/app/app.py
