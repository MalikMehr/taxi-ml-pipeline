import os
import boto3
import pandas as pd
from io import BytesIO
from fastapi import FastAPI
from sklearn.linear_model import LinearRegression

app = FastAPI(title="Taxi ML Service")

# 1. MinIO Configuration
S3_ENDPOINT = "http://minio:9000"
BUCKET_NAME = "gold"
FILE_PATH = "taxi_ml_features" # Spark saves as a directory

s3 = boto3.client('s3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id='admin',
    aws_secret_access_key='password123',
    region_name='us-east-1'
)

# Global model variables
model_fare = None
model_demand = None

def train_models():
    global model_fare, model_demand
    print("🤖 Training models from Gold Layer data...")
    
    try:
        # Pull the gold data (listing files in the gold directory)
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=FILE_PATH)
        # Find the first actual parquet file in the folder
        parquet_file = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.parquet')][0]
        
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=parquet_file)
        df = pd.read_parquet(BytesIO(obj['Body'].read()))

        # --- MODEL 1: FARE REGRESSION ---
        # Features: hour_of_day, day_of_week | Target: avg_total_amount
        X_fare = df[['hour_of_day', 'day_of_week']]
        y_fare = df['avg_total_amount']
        model_fare = LinearRegression().fit(X_fare, y_fare)

        # --- MODEL 2: DEMAND FORECASTING ---
        # Features: hour_of_day | Target: total_trips
        X_demand = df[['hour_of_day']]
        y_demand = df['total_trips']
        model_demand = LinearRegression().fit(X_demand, y_demand)
        
        print("✅ Models trained and ready!")
    except Exception as e:
        print(f"❌ Error training models: {e}")

# Run training on startup
@app.on_event("startup")
async def startup_event():
    train_models()

@app.get("/")
def home():
    status = "Ready" if model_fare else "Models Not Loaded"
    return {"status": status, "source": "MinIO Gold Layer"}

@app.get("/predict/fare")
def predict_fare(hour: int, day_of_week: int):
    if not model_fare: return {"error": "Model not ready"}
    
    prediction = model_fare.predict([[hour, day_of_week]])
    return {"predicted_fare": round(float(prediction[0]), 2), "unit": "USD"}

@app.get("/predict/demand")
def predict_demand(hour: int):
    if not model_demand: return {"error": "Model not ready"}
    
    prediction = model_demand.predict([[hour]])
    return {"predicted_trip_count": int(prediction[0])}