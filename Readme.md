# Flight Price Pipeline Project (flight\_price\_richard)

An automated data pipeline using Apache Airflow and Docker that processes flight price data, ensuring data ingestion, validation, transformation, and loading.

## Project Overview

* **Objective:** Automate data processing for flight prices in Bangladesh, including ingestion, validation, transformation (average fare by airline), and storage in PostgreSQL.
* **Technologies:**

  * Apache Airflow (2.8.1) for orchestration
  * Docker for containerization
  * MySQL (staging database), PostgreSQL (analytics database)
  * Python (pandas, sqlalchemy, python-dotenv)

## Project Structure

* `dags/flight_price_richard.py`: Airflow DAG defining the workflow.
* `scripts/`: Contains Python scripts for each stage (ingestion, validation, transformation, loading).
* `data/`: Directory for CSV dataset (Flight\_Price\_Dataset\_of\_Bangladesh.csv).
* `docker-compose.yml`: Docker services setup.
* `.env`: Environment variables (database credentials).

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd flight_price_richard
   ```
2. **Start Docker Containers:**

   ```bash
   docker-compose up -d
   ```
3. **Access Airflow UI:**

   * URL: [http://localhost:8080](http://localhost:8080)
   * Default credentials: `admin / admin`

## Pipeline Details

* **DAG:** `flight_price_richard`
* **Schedule:** Daily (@daily)
* **Tasks:**

  1. `ingest_data`: Reads CSV and loads into MySQL.
  2. `validate_data`: Checks data quality.
  3. `transform_data`: Calculates average fare by airline.
  4. `load_data`: Stores results in PostgreSQL.

## KPI: Average Fare by Airline

* **Calculation:** Average of `Total Fare (BDT)` for each airline.
* **Output:** Stored in PostgreSQL (`avg_fare_by_airline` table).

## Challenges and Resolutions

1. **Container Setup Issues:** Fixed `docker-compose.yml` (updated image, ports, volumes).
2. **Environment Errors:** Added default values for missing `.env` variables.
3. **ModuleNotFoundError:** Added script path using `sys.path.append`.
4. **Empty Logs:** Redirected container logs using `docker-compose logs`.

## Conclusion

This pipeline automates flight price analysis with scalable, containerized components. It calculates key insights (average fare by airline) and stores them in a PostgreSQL database for further analysis.
