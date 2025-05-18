
import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Add the scripts directory to the Python module search path
# This allows importing functions from scripts/ directory within the container
sys.path.append('/opt/airflow/scripts')

# Define the ingestion function to load CSV data into MySQL
def ingest_data():
    from data_ingestion import ingest_data  # Import the ingestion function
    ingest_data()  # Execute the ingestion process

# Define the validation function to check data quality
def validate_data():
    from data_validation import validate_data  # Import the validation function
    validate_data()  # Execute the validation process

# Define the transformation function to process data
def transform_data():
    from data_transformation import transform_data  # Import the transformation function
    transform_data()  # Execute the transformation process

# Define the loading function to transfer data to PostgreSQL
def load_data():
    from data_loading import load_data  # Import the loading function
    load_data()  # Execute the loading process

# Define default arguments for the DAG, controlling behavior like retries and notifications
default_args = {
    'owner': 'airflow',  # Owner of the DAG for accountability
    'depends_on_past': False,  # Do not depend on previous runs
    'email_on_failure': False,  # Disable email notifications on failure
    'email_on_retry': False,  # Disable email notifications on retry
    'retries': 1,  # Retry once if the task fails
}

# Define the DAG with a unique name reflecting your contribution
with DAG(
    'flight_price_Richard_Amasah',  # Unique DAG ID to show your work in the Airflow UI
    default_args=default_args,  # Apply the default arguments
    description='A pipeline by richard to ingest, validate, transform, and load flight price data',  # Brief description
    schedule_interval='@daily',  # Schedule to run daily at midnight
    start_date=datetime(2025, 5, 18),  # Start date for the DAG
    catchup=False,  # Do not backfill missed runs
) as dag:

    # Define the ingestion task
    ingest_task = PythonOperator(
        task_id='ingest_data',  # Unique identifier for the ingestion task
        python_callable=ingest_data,  # Function to execute
    )

    # Define the validation task
    validate_task = PythonOperator(
        task_id='validate_data',  # Unique identifier for the validation task
        python_callable=validate_data,  # Function to execute
    )

    # Define the transformation task
    transform_task = PythonOperator(
        task_id='transform_data',  # Unique identifier for the transformation task
        python_callable=transform_data,  # Function to execute
    )

    # Define the loading task
    load_task = PythonOperator(
        task_id='load_data',  # Unique identifier for the loading task
        python_callable=load_data,  # Function to execute
    )

    # Set task dependencies: ingestion -> validation -> transformation -> loading
    ingest_task >> validate_task >> transform_task >> load_task