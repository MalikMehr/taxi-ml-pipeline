from pyspark.sql import SparkSession

# Initialize Spark with MinIO (S3) Settings
spark = SparkSession.builder \
    .appName("SilverTransformation") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# 1. Load the Bronze Data
print("📥 Loading Bronze data...")
raw_df = spark.read.parquet("s3a://raw/yellow_tripdata_2024-01.parquet")
raw_df.createOrReplaceTempView("raw_taxi")

# 2. Perform Silver Transformation (Clean, Cast, Deduplicate)
print("⚙️ Running Silver Transformations (Deduplicating & Cleaning)...")

silver_df = spark.sql("""
    SELECT DISTINCT -- <--- THIS REMOVES DUPLICATE ROWS
        -- 1. Correct Data Types (Casting)
        CAST(VendorID AS INT) as vendor_id,
        CAST(tpep_pickup_datetime AS TIMESTAMP) as pickup_time,
        CAST(tpep_dropoff_datetime AS TIMESTAMP) as dropoff_time,
        
        -- 2. Handle Nulls in non-critical columns
        COALESCE(CAST(passenger_count AS INT), 1) as passenger_count,
        COALESCE(CAST(trip_distance AS DOUBLE), 0.0) as trip_distance,
        
        -- 3. Financial Columns
        CAST(fare_amount AS DOUBLE) as fare_amount,
        CAST(tip_amount AS DOUBLE) as tip_amount,
        CAST(total_amount AS DOUBLE) as total_amount,
        
        -- 4. Derived Data
        ROUND((UNIX_TIMESTAMP(tpep_dropoff_datetime) - UNIX_TIMESTAMP(tpep_pickup_datetime)) / 60, 2) as duration_minutes
        
    FROM raw_taxi
    WHERE 
        -- 5. CRITICAL NULL CHECK (Remove rows missing essential data)
        VendorID IS NOT NULL 
        AND tpep_pickup_datetime IS NOT NULL 
        AND tpep_dropoff_datetime IS NOT NULL
        
        -- 6. LOGICAL FILTERS
        AND trip_distance > 0 
        AND passenger_count > 0 
        AND total_amount > 0
""")

# 3. Save to Silver Bucket
print("📤 Writing to Silver Layer...")
silver_df.write.mode("overwrite").parquet("s3a://silver/yellow_taxi_cleaned")

print("✨ SUCCESS: Silver Layer is unique, clean, and cast!")