# Import required libraries for data processing, database interaction, logging, and environment variable management
import pandas as pd
import logging
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file to securely access database credentials
load_dotenv()

# Configure logging to track the transformation process
# Logs are written to both a file (/opt/airflow/logs/data_transformation.log) and the console (StreamHandler)
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO to capture informational messages
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format: timestamp, level, message
    handlers=[
        logging.FileHandler("/opt/airflow/logs/data_transformation.log"),  # Save logs to a file in the container
        logging.StreamHandler()  # Also print logs to the console
    ]
)
# Create a logger instance named "data_transformation" for this script
logger = logging.getLogger("data_transformation")

# Define the transformation function to process data from MySQL and save the result
# Parameters: source_table (MySQL table with raw data), target_table (MySQL table for transformed data)
def transform_data(source_table="flight_data_staging", target_table="flight_data_transformed"):
    try:
        # Construct the MySQL connection string using SQLAlchemy's format
        # Uses environment variables with default fallbacks for user, password, host, port, and database
        mysql_conn_string = (
            f"mysql+mysqlconnector://{os.getenv('MYSQL_USER', 'flight_user')}:{os.getenv('MYSQL_PASSWORD', 'flight_pass')}"
            f"@{os.getenv('MYSQL_HOST', 'mysql')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE', 'flight_staging')}"
        )
        # Create a SQLAlchemy engine to connect to the MySQL database
        engine = create_engine(mysql_conn_string)
        # Log successful connection to MySQL
        logger.info("Connected to MySQL for transformation")

        # Load the raw data from the specified MySQL staging table into a pandas DataFrame
        df = pd.read_sql_table(source_table, engine)
        # Log the number of rows loaded for transformation
        logger.info(f"Loaded {len(df)} rows for transformation")

        # Perform transformation: Calculate the average fare by airline
        # Group by "Airline" and compute the mean of "Total Fare (BDT)"
        avg_fare_by_airline = df.groupby("Airline")["Total Fare (BDT)"].mean().reset_index()
        # Rename columns for clarity in the transformed dataset
        avg_fare_by_airline.columns = ["Airline", "Average_Fare_BDT"]

        # Save the transformed data back to a new MySQL table
        # if_exists="replace" overwrites the table if it already exists; index=False excludes the DataFrame index
        avg_fare_by_airline.to_sql(target_table, con=engine, if_exists="replace", index=False)
        # Log the successful saving of transformed data
        logger.info(f"Transformed data saved to {target_table} with {len(avg_fare_by_airline)} rows")

    # Handle any exceptions that might occur during the transformation process
    except Exception as e:
        # Log any errors that occur (e.g., database connection issues, data processing errors)
        logger.error(f"Transformation error: {e}")
        raise  # Re-raise the exception to fail the task

# Entry point of the script: run the transform_data function if the script is executed directly
if __name__ == "__main__":
    transform_data()