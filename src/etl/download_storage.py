"""
This module downloads to your local machine all of the JSON files that are
stored in Google Cloud Storage via the Google Cloud API. The files are
downloaded into /data/A or B as denoted by the filenames.

Author M. Sanchez-Ayala (04/13/2020)
"""
import logging
import os
import json
from google.cloud import storage
from config import *


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


def get_blobs(bucket):
    """
    Returns
    -------
    blobs: [list] Blob obects from Google Cloud Storage container that hold
    the JSON files we want to download.

    Parameters
    ----------
    ## project: [str] The 12-digit numerical project-id.

    bucket: [str] The name of the bucket.

    """
    # # Establish connection to Google client and open blobs
    # client = storage.Client(
    #     # project = project
    # )
    # bucket = client.get_bucket(bucket)
    # blobs = list(bucket.list_blobs(prefix='data'))

    client = storage.Client.create_anonymous_client()

    bucket = client.bucket('g-maps')

    blobs = list(bucket.list_blobs(prefix='data'))

    return blobs


def download_blobs(blobs, folder):
    """
    Downloads each individual JSON file within the blobs.

    Parameters
    ----------
    blobs: List of Google Cloud Storage blob objects

    folder: [str] the filepath to where we want to save the JSON files.
    """
    # Iterate through all blobs to downlaod
    for i, blob in enumerate(blobs, 1):
        # logging.info('File: {}'.format(blob.name))
        destination_uri = '{}/{}'.format(folder, blob.name)
        with open(destination_uri, "wb") as file_obj:
            blob.download_to_file(file_obj, raw_download=True)
        # logging.info('Exported {} to {}'.format(
        #    blob.name, destination_uri)
        # )
        print('{}/{} files saved.'.format(i, len(blobs)))


def main(bucket, folder):
    """
    Downloads JSON data files from Google Cloud Storage that were stored using
    data_collection.py.

    Parameters
    ----------
    bucket: [str] The name of the bucket.

    folder: [str] the filepath to where we want to save the JSON files.
    """
    # Set up logging for monitoring this process. The logging lines output a lot of annoying
    # code that you can comment out if you so desire.
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # Get a list of blob objects using the Google Cloud Storage API
    blobs = get_blobs(bucket)

    logging.info('Starting download')

    # Create subdirectories to download to if not yet exist
    establish_directories()

    # Download to this directory
    download_blobs(blobs, folder)


if __name__ == '__main__':
    main(config.bucket, config.folder)
