import os
import sys

import pandas as pd
from scipy.stats import ks_2samp

from NetworkSecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from NetworkSecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
)
from NetworkSecurity.entity.config_entity import DataValidationConfig
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


class DataValidation:
    def __init__(
        self,
        data_ingestion_artifact: DataIngestionArtifact,
        data_validation_config: DataValidationConfig,
    ):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self.schema_config["columns"])
            logging.info("Required number of columns: %s", number_of_columns)
            logging.info("Dataframe has columns: %s", len(dataframe.columns))
            return len(dataframe.columns) == number_of_columns
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def detect_dataset_drift(
        self,
        base_df: pd.DataFrame,
        current_df: pd.DataFrame,
        threshold: float = 0.05,
    ) -> bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report[column] = {
                    "p_value": float(is_same_dist.pvalue),
                    "drift_status": is_found,
                }

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report, replace=True)
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                raise Exception(
                    "Train dataframe does not have the required number of columns."
                )
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                raise Exception(
                    "Test dataframe does not have the required number of columns."
                )

            status = self.detect_dataset_drift(
                base_df=train_dataframe, current_df=test_dataframe
            )

            os.makedirs(
                os.path.dirname(self.data_validation_config.valid_train_file_path),
                exist_ok=True,
            )

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path,
                index=False,
                header=True,
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,
                index=False,
                header=True,
            )

            return DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
  


