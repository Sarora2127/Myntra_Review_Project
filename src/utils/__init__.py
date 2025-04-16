# src > utils > __init__.py
from src.cloud_io import MongoIO
from src.constants import MONGO_DATABASE_NAME
from src.exception import CustomException
import os, sys

def fetch_product_names_from_cloud():
    try:
        mongo=MongoIO()  # This creates an instance of the MongoIO class
        collection_names = mongo.mongo_ins.mongo_operation_connect_database.list_collection_names()
        # mongo.mongo_ins.mongo_operation_connect_database probably returns a reference to the connected MongoDB database.
        # .list_collection_names() fetches a list of all collection names from the database.
        return [collection_name.replace('_',' ')
            for collection_name in collection_names]
    except Exception as e:
        raise CustomException(e,sys)