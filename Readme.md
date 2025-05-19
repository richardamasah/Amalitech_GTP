# Flight Price Pipeline Project  

An automated data pipeline using Apache Airflow and Docker that processes flight price data, ensuring data ingestion, validation, transformation, and loading. This project is designed to provide clear, reproducible insights using a fully containerized setup.

## Project Overview

* **Objective:** Automate data processing for flight prices in Bangladesh, covering data ingestion, validation, transformation (average fare by airline), and storage in PostgreSQL for analytics.
* **Key Benefits:**

  * Fully automated data pipeline with minimal manual intervention.
  * Scalable and containerized setup using Docker for easy deployment.
  * Clear data insights stored in an analytics database (PostgreSQL).

## Why This Project Matters

Accurate flight pricing analysis is essential for understanding market trends, optimizing pricing strategies, and making informed business decisions. This project automates the entire workflow, ensuring consistent and reliable data processing without manual intervention.

## Technologies Used

* **Apache Airflow (2.8.1):** Workflow orchestration, scheduling, and monitoring.
* **Docker:** Containerization of the entire setup for consistency.
* **MySQL:** Staging database for raw and intermediate data.
* **PostgreSQL:** Analytics database for final KPIs and reports.
* **Python:** Data processing with `pandas`, `sqlalchemy`, and `python-dotenv`.

## Project Structure

* `dags/flight_price_richard.py`: Defines the Airflow DAG and task dependencies.
* `scripts/`: Python scripts for each stage of the pipeline:

  * `data_ingestion.py`: Reads CSV and loads data into MySQL.
  * `data_validation.py`: Validates data (no missing values, valid durations).
  * `data_transformation.py`: Calculates average fare by airline.
  * `data_loading.py`: Loads results into PostgreSQL.
* `data/`: Directory containing the input dataset (Flight\_Price\_Dataset\_of\_Bangladesh.csv).
* `docker-compose.yml`: Configures Docker containers (Airflow, MySQL, PostgreSQL).
* `.env`: Manages environment variables (database credentials, ports).

## Setup Instructions

```bash
# Clone the Repository
git clone <repository-url>
cd flight_price_richard

# Configure Environment Variables
cp .env.example .env

# Start Docker Containers
docker-compose up -d

# Access Airflow UI
open http://localhost:8080
```

## Sample Code Snippets

* **CSV Ingestion (data\_ingestion.py):**

```python
import pandas as pd
from sqlalchemy import create_engine

def ingest_data():
    df = pd.read_csv('data/Flight_Price_Dataset_of_Bangladesh.csv')
    engine = create_engine('mysql+mysqlconnector://user:pass@localhost:3306/flight_data')
    df.to_sql('flight_data_staging', engine, if_exists='replace', index=False)
```

* **Data Transformation (data\_transformation.py):**

```python
import pandas as pd

def transform_data(df):
    avg_fare_by_airline = df.groupby('Airline')['Total Fare (BDT)'].mean().reset_index()
    avg_fare_by_airline.columns = ['Airline', 'Average_Fare_BDT']
    return avg_fare_by_airline
```

* **Data Loading (data\_loading.py):**

```python
from sqlalchemy import create_engine

def load_data(df):
    engine = create_engine('postgresql://analytics_user:password@localhost:5432/flight_analytics')
    df.to_sql('avg_fare_by_airline', engine, if_exists='replace', index=False)
```

## Pipeline Details

* **DAG:** `flight_price_richard`
* **Schedule:** Runs daily at midnight (@daily).
* **Tasks:**

  1. `ingest_data`: Reads CSV and loads it into MySQL.
  2. `validate_data`: Checks data quality and consistency.
  3. `transform_data`: Calculates average fare by airline.
  4. `load_data`: Stores results in PostgreSQL for analytics.

## Challenges and Resolutions

1. **Container Setup Issues:** Corrected `docker-compose.yml` (updated image, ports, volumes).
2. **Environment Errors:** Added default values for missing `.env` variables, ensuring smooth connections.
3. **ModuleNotFoundError:** Fixed import paths using `sys.path.append` for custom scripts.
4. **Empty Logs:** Enabled log capture using `docker-compose logs` and redirected logs to files.

## Best Practices Implemented

* Modular design with separate scripts for each pipeline stage.
* Secure environment variable management using `.env`.
* Clear and consistent logging for debugging and monitoring.
* Scalability through containerized setup (Docker).

## Future Improvements

* Add data visualization (Grafana) for real-time KPI monitoring.
* Implement advanced data validation using custom Airflow operators.
* Set up automated email alerts for pipeline failures.
* Add automated testing for each stage of the pipeline.

## Conclusion

This Flight Price Pipeline provides a robust, scalable solution for automated data processing using Airflow and Docker. It ensures clear data insights, such as the average fare by airline, stored in a PostgreSQL analytics database for further analysis. The modular design allows for easy expansion, making it adaptable for additional datasets or enhanced analytics.
