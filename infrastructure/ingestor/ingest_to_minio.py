import boto3
import os
from botocore.client import Config
from boto3.s3.transfer import TransferConfig

# Using the IP address bypasses the 'underscore' naming restriction in Boto3
ENDPOINT = "http://minio:9000"
KEY = "admin"
SECRET = "password123"
BUCKET = "raw"
DATA_DIR = "/app/Data/raw"

def upload_parquet_data():
    print(f"--- Starting Data Ingestion to {ENDPOINT} ---")
    try:
        # CONNECTION SETTINGS (Keep this exactly as is)
        s3 = boto3.resource('s3',
            endpoint_url=ENDPOINT,
            aws_access_key_id=KEY,
            aws_secret_access_key=SECRET,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            ),
            region_name='us-east-1'
        )

        bucket = s3.Bucket(BUCKET)
        # Check connection
        bucket.meta.client.head_bucket(Bucket=BUCKET)
        print(f"✅ Connected to MinIO!")
    except Exception as e:
        if "404" in str(e):
            print(f"🔨 Creating bucket: {BUCKET}")
            s3.create_bucket(Bucket=BUCKET)
        else:
            print(f"❌ Connection Error: {e}")
            return

    # SHIPPING SETTINGS (The fix for your 47MB file)
    transfer_config = TransferConfig(
        multipart_threshold=1024 * 25, 
        max_concurrency=10,
        multipart_chunksize=1024 * 25, 
        use_threads=True
    )

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.parquet')]
    if not files:
        print(f"⚠️ No files found in {DATA_DIR}")
        return

    for file_name in files:
        print(f"📦 Transferring {file_name} to {BUCKET}...")
        # Add 'Config=transfer_config' here to solve the Access Denied issue
        bucket.upload_file(
            os.path.join(DATA_DIR, file_name), 
            file_name,
            Config=transfer_config
        )
    
    print("\n🚀 SUCCESS: Data is in MinIO!")

if __name__ == "__main__":
    upload_parquet_data()