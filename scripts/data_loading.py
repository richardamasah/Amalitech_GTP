# Import required libraries for data processing, database interaction, logging, and environment variable management
import pandas as pd
import logging
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file to securely access database credentials
load_dotenv()

# Configure logging to track the loading process
# Logs are written to both a file (/opt/airflow/logs/data_loading.log) and the console (StreamHandler)
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO to capture informational messages
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format: timestamp, level, message
    handlers=[
        logging.FileHandler("/opt/airflow/logs/data_loading.log"),  # Save logs to a file in the container
        logging.StreamHandler()  # Also print logs to the console
    ]
)
# Create a logger instance named "data_loading" for this script
logger = logging.getLogger("data_loading")

# Define the loading function to transfer transformed data from MySQL to PostgreSQL
# Parameters: source_table (MySQL table with transformed data), target_table (PostgreSQL table to store the data)
def load_data(source_table="flight_data_transformed", target_table="avg_fare_by_airline"):
    try:
        # Construct the MySQL connection string using SQLAlchemy's format
        # Uses environment variables with default fallbacks for user, password, host, port, and database
        mysql_conn_string = (
            f"mysql+mysqlconnector://{os.getenv('MYSQL_USER', 'flight_user')}:{os.getenv('MYSQL_PASSWORD', 'flight_pass')}"
            f"@{os.getenv('MYSQL_HOST', 'mysql')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE', 'flight_staging')}"
        )
        # Create a SQLAlchemy engine to connect to the MySQL database (source of transformed data)
        mysql_engine = create_engine(mysql_conn_string)
        # Log successful connection to MySQL
        logger.info("Connected to MySQL for loading")

        # Load the transformed data from the specified MySQL table into a pandas DataFrame
        df = pd.read_sql_table(source_table, mysql_engine)
        # Log the number of rows loaded from the source table
        logger.info(f"Loaded {len(df)} rows from {source_table}")

        # Construct the PostgreSQL connection string using SQLAlchemy's format
        # Uses environment variables with default fallbacks for user, password, host, port, and database
        pg_conn_string = (
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'analytics_user')}:{os.getenv('POSTGRES_PASSWORD', 'analytics_pass')}"
            f"@{os.getenv('POSTGRES_HOST', 'analytics-postgres')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DATABASE', 'flight_analytics')}"
        )
        # Create a SQLAlchemy engine to connect to the PostgreSQL database (target for analytics data)
        pg_engine = create_engine(pg_conn_string)
        # Log successful connection to PostgreSQL
        logger.info("Connected to PostgreSQL for loading")

        # Load the DataFrame into the specified PostgreSQL table
        # if_exists="replace" overwrites the table if it already exists; index=False excludes the DataFrame index
        df.to_sql(target_table, pg_engine, if_exists="replace", index=False)
        # Log the successful loading of data into PostgreSQL
        logger.info(f"Loaded {len(df)} rows into {target_table} in PostgreSQL")

    # Handle any exceptions that might occur during the loading process
    except Exception as e:
        # Log any errors that occur (e.g., database connection issues, table not found)
        logger.error(f"Loading error: {e}")
        raise  # Re-raise the exception to fail the task

# Entry point of the script: run the load_data function if the script is executed directly
if __name__ == "__main__":
    load_data()