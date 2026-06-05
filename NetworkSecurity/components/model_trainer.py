import os
import sys
import tempfile

os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 1))

import mlflow
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from NetworkSecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact,
)
from NetworkSecurity.entity.config_entity import ModelTrainerConfig
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.utils.main_utils.utils import (
    evaluate_models,
    load_numpy_array_data,
    load_object,
    save_object,
)
from NetworkSecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score,
)
from NetworkSecurity.utils.ml_utils.model.estimator import NetworkModel


class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact,
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        

    def tracking_mlflow(self, best_model, classification_train_metric, classification_test_metric):
        mlflow_tmp_dir = os.path.abspath(os.path.join("mlruns", "tmp"))
        os.makedirs(mlflow_tmp_dir, exist_ok=True)
        os.environ["TMP"] = mlflow_tmp_dir
        os.environ["TEMP"] = mlflow_tmp_dir
        os.environ["TMPDIR"] = mlflow_tmp_dir
        tempfile.tempdir = mlflow_tmp_dir

        with mlflow.start_run():
            mlflow.log_param("model_name", best_model.__class__.__name__)
            mlflow.log_metric("train_f1_score", classification_train_metric.f1_score)
            mlflow.log_metric(
                "train_precision_score",
                classification_train_metric.precision_score,
            )
            mlflow.log_metric("train_recall_score", classification_train_metric.recall_score)
            mlflow.log_metric("test_f1_score", classification_test_metric.f1_score)
            mlflow.log_metric(
                "test_precision_score",
                classification_test_metric.precision_score,
            )
            mlflow.log_metric("test_recall_score", classification_test_metric.recall_score)
            mlflow.sklearn.log_model(sk_model=best_model, name="model")

    def train_model(self, x_train, y_train, x_test, y_test) -> ModelTrainerArtifact:
        try:
            models = {
                "Logistic Regression": LogisticRegression(max_iter=1000),
                "Random Forest": RandomForestClassifier(),
                "KNN": KNeighborsClassifier(),
                "Decision Tree": DecisionTreeClassifier(),
                "AdaBoost": AdaBoostClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(),
            }

            params = {
                "Decision Tree": {"criterion": ["gini", "entropy"]},
                "Random Forest": {
                    "criterion": ["gini", "entropy"],
                    "n_estimators": [8, 16, 32, 64],
                },
                "KNN": {"n_neighbors": [5, 7, 9, 11]},
                "Gradient Boosting": {
                    "learning_rate": [0.1, 0.01, 0.05],
                    "subsample": [0.7, 0.8, 0.9],
                    "n_estimators": [8, 16, 32],
                },
                "AdaBoost": {
                    "learning_rate": [0.1, 0.01, 0.05],
                    "n_estimators": [8, 16, 32],
                },
                "Logistic Regression": {},
            }

            model_report = evaluate_models(
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
                models=models,
                param=params,
            )

            best_model_score = max(model_report.values())
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]
            logging.info("Best model: %s (f1=%.4f)", best_model_name, best_model_score)

            if best_model_score < self.model_trainer_config.expected_score:
                raise Exception(
                    f"No best model found with score above "
                    f"{self.model_trainer_config.expected_score}"
                )

            y_train_pred = best_model.predict(x_train)
            y_test_pred = best_model.predict(x_test)

            classification_train_metric = get_classification_score(
                y_true=y_train, y_pred=y_train_pred
            )
            classification_test_metric = get_classification_score(
                y_true=y_test, y_pred=y_test_pred
            )

            ##Track ML Flow
            self.tracking_mlflow(
                best_model, classification_train_metric, classification_test_metric
            )

            preprocessor = load_object(
                file_path=self.data_transformation_artifact.preprocessor_object_file_path
            )
            network_model = NetworkModel(preprocessor=preprocessor, model=best_model)

            model_dir = os.path.dirname(
                self.model_trainer_config.trained_model_file_path
            )
            os.makedirs(model_dir, exist_ok=True)
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=network_model,
            )

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric,
            )
            logging.info("Model Trainer Artifact: %s", model_trainer_artifact)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )
            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            x_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            x_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            return self.train_model(x_train, y_train, x_test, y_test)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
