# Taxi ML Pipeline: End-to-End Data Engineering Project

**Architect:** Mehr Khan Malik  
**Data Type:** Structured NYC Taxi Trip Records  

## Project Overview
This project implements a **Medallion Architecture** using Dockerized microservices to process taxi data and serve real-time ML predictions.

## Automation (The Proof)
The pipeline is fully automated using **Windows Task Scheduler**.
- **Trigger:** Scheduled daily execution.
- **Action:** Runs `infrastructure/ingestor/Python_run_migration.bat`.
- **Purpose:** Automatically pulls fresh data into the **Bronze Layer** without manual intervention.

## Architectural Pivot: From Airbyte to Python
Initially, **Apache Airbyte** was proposed for ingestion. During the development phase, I pivoted to a **Custom Python Ingestor** for the following reasons:
1. **Resource Efficiency:** Airbyte's Java-based stack was too heavy for local development RAM.
2. **Reliability:** A lightweight Python microservice reduced memory usage by 80%.
3. **Simplicity:** Direct integration with MinIO via `boto3` offered more control.

## API Results
- **Fare Prediction:** $27.88 (Linear Regression)
- **Demand Forecasting:** 2189 trips (Time-series analysis)<img width="1360" height="552" alt="image" src="https://github.com/user-attachments/assets/7098620d-70a8-4df2-8cbd-ba95da093c1f" />
