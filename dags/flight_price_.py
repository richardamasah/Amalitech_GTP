from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.data_ingestion import ingest_data
from scripts.data_validation import validate_data
from scripts.data_transformation import transform_data
from scripts.data_loading import load_to_postgres

CONFIG_PATH = '/opt/airflow/config/config.yaml'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': 300,
}

with DAG(
    'flight_price_pipeline',
    default_args=default_args,
    description='Flight Price Analysis Pipeline for Bangladesh',
    schedule_interval='@daily',
    start_date=datetime(2025, 5, 15),
    catchup=False,
) as dag:
    
    ingest_task = PythonOperator(
        task_id='ingest_data',
        python_callable=ingest_data,
        op_kwargs={'config_path': CONFIG_PATH}
    )
    
    validate_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
        op_kwargs={'config_path': CONFIG_PATH}
    )
    
    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        op_kwargs={'config_path': CONFIG_PATH}
    )
    
    load_task = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_to_postgres,
        op_kwargs={'config_path': CONFIG_PATH}
    )
    
    ingest_task >> validate_task >> transform_task >> load_task