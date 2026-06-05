import sys
import os
import certifi
from mlflow import client

from NetworkSecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME
from NetworkSecurity.utils.ml_utils.model.estimator import NetworkModel
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)
import pymongo
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.pipeline.training_pipeline import TrainingPipeline
from NetworkSecurity.logging.logger import logging

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, Request, UploadFile
from uvicorn import run as app_run
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import pandas as pd 
from dataclasses import asdict

from NetworkSecurity.utils.main_utils.utils import load_object

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)

from NetworkSecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME


database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origin = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route(request: Request):
    try:
        training_pipeline = TrainingPipeline()
        data_ingestion_artifact = training_pipeline.start_data_ingestion()
        data_validation_artifact = training_pipeline.start_data_validation(
            data_ingestion_artifact=data_ingestion_artifact
        )
        data_transformation_artifact = training_pipeline.start_data_transformation(
            data_validation_artifact=data_validation_artifact
        )
        model_trainer_artifact = training_pipeline.start_model_trainer(
            data_transformation_artifact=data_transformation_artifact
        )
        return JSONResponse(
            content={
                "message": "Training successful",
                "model_trainer_artifact": asdict(model_trainer_artifact),
            }
        )
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
@app.post("/predict")
async def predict_route(request: Request, file:UploadFile=File(...)):
    try:
        df = pd.read_csv(file.file)
        preporcesso=load_object("final_model/preprocessor.pkl")
        final_model=load_object("Final_model/model.pkl")
        network_model=NetworkModel(preprocessor=preporcesso, model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['prediction_column']=y_pred
        print(df['prediction_column'])
        output_dir = "predicted_output"
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(os.path.join(output_dir, "output.csv"), index=False)
        table_html = df.to_html(classes="table table-striped")
        return HTMLResponse(content=table_html)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e







if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)