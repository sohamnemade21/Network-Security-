from sklearn.metrics import f1_score
from sklearn.model_selection import GridSearchCV
import yaml
from NetworkSecurity.exception.exception import NetworkSecurityException
import sys
import os
import numpy as np
from NetworkSecurity.logging.logger import logging
#import dill 
import pickle

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as yaml_file:
            yaml.dump(content, yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def save_numpy_array_data(file_path: str, array: np.array) -> None:
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(file_path: str, obj: object) -> None:
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
        logging.info(f"Object saved successfully at {file_path}")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

def load_object(file_path: str) -> object:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        with open(file_path, "rb") as file_obj:
            obj = pickle.load(file_obj)
        logging.info(f"Object loaded successfully from {file_path}")
        return obj
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array_data(file_path: str) -> np.array:
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    

def evaluate_models(x_train, y_train, x_test, y_test, models: dict, param: dict) -> dict:
    try:
        report = {}

        for i in range(len(models)):
            model=list(models.values())[i]
            para=param[list(models.keys())[i]]

            gs = GridSearchCV(model, para, cv=3, scoring="f1")
            gs.fit(x_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(x_train, y_train)

            y_test_pred = model.predict(x_test)

            test_model_score = f1_score(y_test, y_test_pred)

            report[list(models.keys())[i]] = test_model_score
        return report
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e