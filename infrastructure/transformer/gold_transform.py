from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Initialize Spark with MinIO Settings
spark = SparkSession.builder \
    .appName("GoldFeatureEngineering") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# 1. Load Cleaned Silver Data
print("📥 Loading Silver data...")
# 1. Load Silver Data
silver_df = spark.read.parquet("s3a://silver/yellow_taxi_cleaned")
silver_df.createOrReplaceTempView("silver_taxi")

# 2. Create the Dual-Purpose Feature Table
# This table serves both: 
#   - Regression (Predicting 'avg_total_amount')
#   - Forecasting (Predicting 'total_trips')
gold_df = spark.sql("""
    SELECT 
        vendor_id,
        date_trunc('hour', pickup_time) as pickup_hour,
        
        -- Time Features (Crucial for ML)
        hour(pickup_time) as hour_of_day,
        dayofweek(pickup_time) as day_of_week,
        CASE WHEN dayofweek(pickup_time) IN (1, 7) THEN 1 ELSE 0 END as is_weekend,
        
        -- Model 1 Target & Features: Demand Forecasting
        COUNT(*) as total_trips,
        
        -- Model 2 Target & Features: Fare Regression
        ROUND(AVG(total_amount), 2) as avg_total_amount,
        ROUND(AVG(trip_distance), 2) as avg_distance,
        ROUND(AVG(duration_minutes), 2) as avg_duration,
        
        -- Bonus Feature: Efficiency (Revenue per Minute)
        ROUND(SUM(total_amount) / SUM(duration_minutes), 2) as rev_per_minute
        
    FROM silver_taxi
    GROUP BY vendor_id, pickup_hour, hour_of_day, day_of_week, is_weekend
    ORDER BY pickup_hour ASC
""")

# 3. Save to Gold
print("📤 Writing Dual-Model Features to Gold Layer...")
gold_df.write.mode("overwrite").parquet("s3a://gold/taxi_ml_features")
print("✨ GOLD SUCCESS: Features ready for Regression & Forecasting!")