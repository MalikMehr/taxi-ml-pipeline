# Use a lightweights Python 'base'
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the Boto3 library inside the container
RUN pip install --no-cache-dir boto3

# COPY the script from your computer INTO the container image
COPY ingest_to_minio.py .

# The command to run when the container starts
CMD ["python", "ingest_to_minio.py"]