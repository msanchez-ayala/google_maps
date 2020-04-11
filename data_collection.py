"""
This module uses the Directions class to call the Google Maps API for trip
directions between two locations. It then saves those directions as JSON files
in a subdirectory within this one.
"""
import os
from directions import Directions
import config


def establish_directories():
    """
    Checks if the necessary data-storing directories exist. If not, creates them
    within the current directory.
    """
    if not os.path.exists('data'):
        os.mkdir('data')
        os.mkdir('data/A')
        os.mkdir('data/B')
    elif (not os.path.exists('data/A')) or (not os.path.exists('data/B')):
        os.mkdir('data/A')
        os.mkdir('data/B')


def main():
    """
    Creates the correct subdirectories in which to store collected data,
    instantiates a Directions object to collect data from the Google Maps API,
    and saves each trip direction as a JSON in the subdirectories defined
    above.
    """
    establish_directories()
    
    directions = Directions(config.location_A, config.location_B)

    # Save JSON files
    directions.to_json(directions.directions_A, 'data/A/')
    directions.to_json(directions.directions_B, 'data/B/')

if __name__ == '__main__':
    main()
