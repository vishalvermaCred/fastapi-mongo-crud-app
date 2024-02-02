from ast import literal_eval
from os import getenv

from dotenv import find_dotenv, load_dotenv

from app.constants import DB_NAME

load_dotenv(find_dotenv())

BASE_ROUTE = getenv("BASE_ROUTE")
SERVICE_NAME = getenv("SERVICE_NAME")
ENV = getenv("ENV")
LOG_LEVEL = getenv("LOG_LEVEL", "DEBUG")

MongoConfigs = {"uri": getenv("MONGO_URI", "mongodb://localhost:27017"), "db_name": DB_NAME}
