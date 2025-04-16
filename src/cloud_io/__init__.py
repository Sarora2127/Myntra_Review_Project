# src > cloud_io > __init__.py
import pandas as pd
from database_connect import mongo_operation as mongo # type : ignore
import os, sys
from src.constants import *
from src.exception import CustomException

class MongoIO: # used to interact with mongo DB for storing and retrieveing product reviews
    mongo_ins = None # class level attr; establish connection only once during lifetime of the application
    def __init__(self): # constructor
        if MongoIO.mongo_ins is None:
            mongo_db_url = "mongodb+srv://sakshamarora210204:NK0k7TWAZzXLlAWV@cluster0.bvcmmhr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            if mongo_db_url is None:
                raise Exception(f"Environment key: {MONGODB_URL_KEY} is not set.")
            MongoIO.mongo_ins = mongo(client_url = mongo_db_url, database_name= MONGO_DATABASE_NAME)
        self.mongo_ins = MongoIO.mongo_ins

    def store_reviews(self, product_name: str, reviews: pd.DataFrame):
        try:
            collection_name = product_name.replace(" ","_")
            self.mongo_ins.bulk_insert(reviews, collection_name)
        except Exception as e:
            raise CustomException(e, sys)

    def get_reviews(self, product_name: str):
        try:
            data = self.mongo_ins.find(collection_name = product_name.replace(" ","_"))
            data.drop(columns=["_id"], inplace=True, errors="ignore")
            return data
        except Exception as e:
            raise CustomException(e,sys)