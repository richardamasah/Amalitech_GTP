# Import required libraries for data processing, database interaction, logging, and environment variable management
import os
import pandas as pd
from sqlalchemy import create_engine
import logging
from dotenv import load_dotenv

# Load environment variables from .env file to securely access database credentials and file paths
load_dotenv()

# Configure logging to track the ingestion process
# Logs are written to both a file (/opt/airflow/logs/data_ingestion.log) and the console (StreamHandler)
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO to capture informational messages
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format: timestamp, level, message
    handlers=[
        logging.FileHandler("/opt/airflow/logs/data_ingestion.log"),  # Save logs to a file in the container
        logging.StreamHandler()  # Also print logs to the console
    ]
)
# Create a logger instance named "data_ingestion" for this script
logger = logging.getLogger("data_ingestion")

# Define the ingestion function to load CSV data into a MySQL staging database
# Parameters: csv_path (path to the CSV file), table_name (target MySQL table)
def ingest_data(csv_path="/opt/airflow/data/Flight_Price_Dataset_of_Bangladesh.csv", table_name="flight_data_staging"):
    try:
        # Log the start of the CSV reading process
        logger.info(f"Reading CSV from {csv_path}")
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_path)
        # Log the number of rows loaded from the CSV
        logger.info(f"Loaded {len(df)} rows from CSV")

        # Validate that all required columns are present in the DataFrame
        # List of expected columns in the flight price dataset
        required_columns = [
            "Airline", "Source", "Source Name", "Destination", "Destination Name",
            "Departure Date & Time", "Arrival Date & Time", "Duration (hrs)", "Stopovers",
            "Aircraft Type", "Class", "Booking Source", "Base Fare (BDT)",
            "Tax & Surcharge (BDT)", "Total Fare (BDT)", "Seasonality", "Days Before Departure"
        ]
        # Identify any missing columns by comparing required columns with DataFrame columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        # If there are missing columns, log an error and raise an exception
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Retrieve MySQL connection details from environment variables with default fallbacks
        # This ensures the script can proceed even if some variables are missing in .env
        mysql_user = os.getenv("MYSQL_USER", "flight_user")
        mysql_password = os.getenv("MYSQL_PASSWORD", "flight_pass")
        mysql_host = os.getenv("MYSQL_HOST", "mysql")
        mysql_port = os.getenv("MYSQL_PORT", "3306")  # Default MySQL port if not specified
        mysql_database = os.getenv("MYSQL_DATABASE", "flight_staging")

        # Log the connection details for debugging purposes (excluding the password for security)
        logger.info(f"Connecting to MySQL - Host: {mysql_host}, Port: {mysql_port}, User: {mysql_user}, Database: {mysql_database}")

        # Construct the MySQL connection string using SQLAlchemy's format
        # Format: mysql+mysqlconnector://user:password@host:port/database
        mysql_conn_string = (
            f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        )
        # Create a SQLAlchemy engine to connect to the MySQL database
        engine = create_engine(mysql_conn_string)

        # Load the DataFrame into the specified MySQL table
        # if_exists="replace" overwrites the table if it already exists; index=False excludes the DataFrame index
        df.to_sql(table_name, con=engine, if_exists="replace", index=False)
        # Log the successful loading of data into MySQL
        logger.info(f"Successfully loaded {len(df)} rows into {table_name}")

    # Handle specific exceptions that might occur during ingestion
    except FileNotFoundError as e:
        # Log an error if the CSV file is not found at the specified path
        logger.error(f"CSV file not found: {e}")
        raise  # Re-raise the exception to fail the task
    except ValueError as e:
        # Log an error if validation fails (e.g., missing columns)
        logger.error(f"Validation error: {e}")
        raise  # Re-raise the exception to fail the task
    except Exception as e:
        # Log any other unexpected errors during the ingestion process
        logger.error(f"Error loading data to MySQL: {e}")
        raise  # Re-raise the exception to fail the task

# Entry point of the script: run the ingest_data function if the script is executed directly
if __name__ == "__main__":
    ingest_data()