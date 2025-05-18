# Challenges Encountered and How They Were Resolved

## 1. Initial Container Setup Issues

* **Issue:** Containers failed to start due to misconfiguration in `docker-compose.yml`.
* **Resolution:**

  * Updated `docker-compose.yml` to use `apache/airflow:2.8.1`.
  * Corrected port mappings (e.g., `0.0.0.0:8080->8080/tcp`).
  * Ensured proper volume mounts (e.g., `./data:/opt/airflow/data`).

## 2. Environment Variable Errors in `data_ingestion.py`

* **Issue:** `ValueError: invalid literal for int() with base 10: 'None'` due to missing `MYSQL_PORT` in `.env` file.
* **Resolution:**

  * Added default values in the script (e.g., `mysql_port = os.getenv("MYSQL_PORT", "3306")`).
  * Logged connection details for debugging, ensuring correct values were loaded.

## 3. ModuleNotFoundError in DAG

* **Issue:** `ModuleNotFoundError: No module named 'scripts.data_ingestion'` when running the DAG.
* **Resolution:**

  * Added `sys.path.append('/opt/airflow/scripts')` in `flight_price_richard.py` to include the `scripts/` directory in the Python path.

## 4. Empty Local Logs

* **Issue:** The local `logs/` folder was empty despite successful DAG runs.
* **Resolution:**

  * Used `docker-compose logs` to capture container logs (e.g., `docker-compose logs airflow-webserver > logs/airflow-webserver.log`).
  * Included these logs in the project repository for easy access and debugging.
