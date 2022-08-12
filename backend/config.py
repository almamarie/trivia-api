import os
from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


# DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
# DB_USER = os.getenv('DB_USER', 'postgres')
# DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
# DB_NAME = os.getenv('DB_NAME', 'trivia')

DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# name =    'postgresql+psycopg2://{}:{}@{}/{}'.format(
#     DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# Enable debug mode.
DEBUG = True

# Connect to the database


SQLALCHEMY_DATABASE_URI = DB_PATH
