# Import required libraries for data processing, database interaction, logging, and environment variable management
import pandas as pd
import logging
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file to securely access database credentials
load_dotenv()

# Configure logging to track the validation process
# Logs are written to both a file (/opt/airflow/logs/data_validation.log) and the console (StreamHandler)
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO to capture informational messages
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format: timestamp, level, message
    handlers=[
        logging.FileHandler("/opt/airflow/logs/data_validation.log"),  # Save logs to a file in the container
        logging.StreamHandler()  # Also print logs to the console
    ]
)
# Create a logger instance named "data_validation" for this script
logger = logging.getLogger("data_validation")

# Define the validation function to check the quality of ingested data in MySQL
# Parameter: table_name (MySQL table containing the ingested data to validate)
def validate_data(table_name="flight_data_staging"):
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
        logger.info(f"Connected to MySQL for validation")

        # Load the ingested data from the specified MySQL table into a pandas DataFrame
        df = pd.read_sql_table(table_name, engine)
        # Log the number of rows loaded for validation
        logger.info(f"Loaded {len(df)} rows for validation")

        # Perform validation checks on the data
        # Initialize a list to store any validation issues
        issues = []
        # Check for missing values in the "Total Fare (BDT)" column
        if df["Total Fare (BDT)"].isnull().any():
            issues.append("Missing values in Total Fare (BDT)")
        # Check if "Duration (hrs)" values are within a valid range (0 to 24 hours)
        if not df["Duration (hrs)"].between(0, 24).all():
            issues.append("Invalid Duration (hrs) values (outside 0-24 range)")
        # Check if "Departure Date & Time" values are in a valid datetime format
        # errors='coerce' converts invalid formats to NaT; notna().all() ensures all values are valid
        if not pd.to_datetime(df["Departure Date & Time"], errors='coerce').notna().all():
            issues.append("Invalid Departure Date & Time format")

        # If there are any validation issues, log them and raise an error
        if issues:
            logger.error(f"Validation failed: {', '.join(issues)}")
            raise ValueError(f"Validation errors: {', '.join(issues)}")
        # If no issues are found, log a success message
        else:
            logger.info("Validation passed successfully")

    # Handle any exceptions that might occur during the validation process
    except Exception as e:
        # Log any errors that occur (e.g., database connection issues, data validation failures)
        logger.error(f"Validation error: {e}")
        raise  # Re-raise the exception to fail the task

# Entry point of the script: run the validate_data function if the script is executed directly
if __name__ == "__main__":
    validate_data()