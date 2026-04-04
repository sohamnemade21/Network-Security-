import os
import sys
import json
from dotenv import load_dotenv
import certifi
import pandas as pd
import pymongo

from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging as logger

# Load environment variables
load_dotenv()

# Get MongoDB URL
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Validate env variable (non-negotiable)
if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URL is not set. Check your .env file.")

# Certifi for secure connection
ca = certifi.where()


class NetworkDataExtract:

    def __init__(self):
        pass

    def csv_to_json_convertor(self, file_path):
        try:
            # Read CSV
            data = pd.read_csv(file_path)

            # Clean index
            data.reset_index(drop=True, inplace=True)

            # Convert to JSON records
            records = list(json.loads(data.T.to_json()).values())

            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            # Connect to MongoDB
            mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)

            db = mongo_client[database]
            collection = db[collection]

            # Insert data
            collection.insert_many(records)

            return len(records)

        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    try:
        # Use forward slashes (cleaner, no escape issues)
        FILE_PATH = "E:/Krish Naik Data science course/Project 2/Network Security/Network_Data/phisingData.csv"

        DATABASE = "nemadesoham21_db"
        COLLECTION = "phisingData"

        networkobj = NetworkDataExtract()

        # Convert CSV → JSON
        records = networkobj.csv_to_json_convertor(FILE_PATH)
        print(f"Records loaded: {len(records)}")

        # Insert into MongoDB
        no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)
        print(f"Inserted into MongoDB: {no_of_records}")

    except Exception as e:
        raise NetworkSecurityException(e, sys)