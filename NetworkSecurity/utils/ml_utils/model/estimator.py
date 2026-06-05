from NetworkSecurity.constants.training_pipeline import SAVED_MODEL_DIR
from NetworkSecurity.constants.training_pipeline import MODEL_FILE_NAME

import sys
import os

from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging

class NetworkModel:
    def __init__(self,preprocessor,model):
        try:
            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def predict(self, X):
        try:
            x_transformed = self.preprocessor.transform(X)
            y_hat = self.model.predict(x_transformed)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
