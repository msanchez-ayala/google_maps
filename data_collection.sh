### FILL IN ### absolute path to the google_maps dir on your local machine
cd path_to_google_maps

# Activate python venv
source ./bin/activate

### FILL IN IF USING CLOUD STORAGE ### absolute path to authorization json
#export GOOGLE_APPLICATION_CREDENTIALS='path_to_your_google_auth.json'

# Collect data
python ./src/etl/data_collection.py

# Close out
deactivate
