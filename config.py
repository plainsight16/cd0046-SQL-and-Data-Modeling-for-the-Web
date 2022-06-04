import os
from urllib.parse import quote_plus as urlquote

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:%s@localhost:5432/fyyur' % urlquote(
    'theceo@16')
SQLALCHEMY_TRACK_MODIFICATIONS = False
