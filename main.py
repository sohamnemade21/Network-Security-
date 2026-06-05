import sys
import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 1))

from NetworkSecurity.components.data_validation import DataValidation 
from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.components.model_trainer import ModelTrainer
from NetworkSecurity.entity.config_entity import (
    DataIngestionConfig, DataValidationConfig,DataTransformationConfig,
    ModelTrainerConfig, TrainingPipelineConfig,
)
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.components.data_transformation import DataTransformation


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
        print(data_validation_artifact)
       
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        logging.info("Starting data transformation.")
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        print("Data transformation completed")

        logging.info("Model training started.")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config, data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        print(model_trainer_artifact)
    
        logging.info("Model Training Artifact created")  
    
    except Exception as e:
        raise NetworkSecurityException(e, sys) 
