import sys
from NetworkSecurity.components.data_validation import DataValidation 
from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.entity.config_entity import (
    DataIngestionConfig, DataValidationConfig,
    TrainingPipelineConfig,
)
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging


if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion artifact: %s", data_ingestion_artifact)
        logging.info("Data Initiation completed successfully.")
        print(data_ingestion_artifact)
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
        logging.info("Starting data validation.")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data validation artifact: %s", data_validation_artifact)
        print(data_ingestion_artifact)
        print(data_validation_artifact)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
