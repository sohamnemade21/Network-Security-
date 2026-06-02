from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.entity.config_entity import DataIngestionConfig
from NetworkSecurity.entity.artifact_entity import DataIngestionArtifact
from NetworkSecurity.logging.logger import logging
import sys
import os
import numpy as np
import pandas as pd
import pymongo
from sklearn.model_selection import train_test_split 

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def export_collection_as_dataframe(self):
        try:
            if not MONGO_DB_URL:
                raise ValueError("MONGO_DB_URL environment variable is not set")

            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]


            df=pd.DataFrame(list(collection.find()))
            if '_id' in df.columns.to_list():
                df = df.drop(columns=['_id']) 

            df.replace({"na":np.nan},inplace=True)
            logging.info("Exported collection %s.%s as dataframe", database_name, collection_name)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_into_feature_store(self, dataframe:pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            logging.info("Saved feature store file at %s", feature_store_file_path)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def split_data_as_train_test(self, dataframe:pd.DataFrame):
        try:
            train_set,test_set=train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42
            )
            train_file_path=self.data_ingestion_config.training_file_path
            test_file_path=self.data_ingestion_config.testing_file_path

            dir_path=os.path.dirname(train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            dir_path=os.path.dirname(test_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_set.to_csv(train_file_path,index=False,header=True)
            test_set.to_csv(test_file_path,index=False,header=True)
            logging.info("Saved train file at %s and test file at %s", train_file_path, test_file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)



    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_collection_as_dataframe()
            dataframe=self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestion_artifact=DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return dataingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
