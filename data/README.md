# Data Collection

The data collection exploration was conducted in **data_collection.ipynb**.

Code from this notebook is split into the following python files:

1. **data_collection.py:** A module that is run every 5 minutes using cron in order
to call the Google Maps API and store relevant data into the MySQL db.
2. **GDirections.py:** The GDirections class.
3. **helpers.py:** Helper functions for **data_collection.py**.

# EDA

The experimental EDA for this project is contained within **eda.ipynb**. 
