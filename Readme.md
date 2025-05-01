


#  Real-Time Data Ingestion Pipeline (E-Commerce Simulation)

This project implements a real-time data ingestion pipeline simulating user activity (e.g., product views, purchases) on an e-commerce platform. It uses **Apache Spark Structured Streaming** to process data in real time and **PostgreSQL** to store it reliably. The pipeline is fully **Dockerized** for seamless deployment and testing.

---

##  Project Structure

```
├── data/events/                   # Folder for generated CSV event files
├── Docs/                          # Documentation and reference files
│   ├── system_architecture.png    # Architecture diagram
│
├── src/                           # Source code scripts
│   ├── data_generator.py          # Fake event generator (CSV output)
│   ├── spark_streaming_to_postgres.py  # Spark Structured Streaming job
│   └── postgres_setup.sql         # SQL to set up PostgreSQL schema
│
├── postgres_connection_details.txt # Host, port, credentials
├── Dockerfile.spark               # Dockerfile for Spark streaming job
├── Dockerfile.generator           # Dockerfile for data generator
├── docker-compose.yml             # Orchestrates Spark, PostgreSQL, generator
├── requirements.txt               # Python dependencies
└── README.md                      # Project overview and usage
```

---

##  Architecture

The pipeline flows as follows:

```
Data Generator (Python)
        ↓
Generated CSV Files (data/events/)
        ↓
Spark Structured Streaming (PySpark)
        ↓
PostgreSQL Database (user_events table)
```

![System Architecture](Docs/system_architecture.png)

---

##  Quick Start

###  Run Locally (Without Docker)

####  Prerequisites
- Python 3.8+
- PostgreSQL 13+
- Apache Spark 3.4.0+
- Java 8 or 11
- Dependencies:
  ```bash
  pip install faker pandas pyspark
  ```
- Place `postgresql-42.6.0.jar` in the project root.

####  Steps
```bash
# 1. Set up PostgreSQL
psql -U postgres -f src/postgres_setup.sql

# 2. Run the data generator
python src/data_generator.py

# 3. Run the Spark streaming job
spark-submit --jars postgresql-42.6.0.jar src/spark_streaming_to_postgres.py
```

---

###  Run with Docker (Recommended)

#### ✅ Prerequisites
- Install Docker Desktop
- Place `postgresql-42.6.0.jar` in the root folder

####  Steps
```bash
docker-compose build
docker-compose up
```

####  Verify
- CSVs: Check `data/events/`
- PostgreSQL:
  ```bash
  psql -h localhost -U postgres -d ecommerce_events
  ```
  Password: `mysecretpassword`
- Spark logs:
  ```bash
  docker-compose logs spark
  ```

####  Stop
```bash
docker-compose down
```

---

##  Performance Metrics

This section summarizes the pipeline's behavior over a 5-minute test run.

### ⏱ Latency
- **Average:** 3.2 seconds
- **Range:** 2.8–3.6 sec
- **Breakdown:**
  - CSV Read: ~0.5 sec
  - Transform: ~1.0 sec
  - JDBC Write: ~1.7 sec

###  Throughput
- **Total events:** 600
- **Throughput:** 2 events/sec
- **Peak:** 2.5 events/sec

###  Resource Usage
- **Spark CPU:** ~20% (2 cores)
- **Spark Memory:** ~4 GB
- **PostgreSQL CPU:** ~10%
- **PostgreSQL Memory:** ~200 MB

###  Scalability
- Scaled up to 10 events/sec with latency ~3.5 sec
- No system crashes or failures

###  Optimizations
- Indexed `user_id`, `event_type`
- Used PostgreSQL default `created_at`
- Recommend: Spark cluster mode, JDBC pooling, lower processing trigger

---

##  Manual Test Cases

| Test Case                 | Action                                                | Expected Outcome                                     | Actual Outcome ✅ |
|--------------------------|--------------------------------------------------------|------------------------------------------------------|-------------------|
| **CSV File Generation**  | Run `data_generator.py` for 10s                        | 2 CSVs with 10 rows each                             | Passed            |
| **Spark File Detection** | Run Spark job while generating files                   | Files detected and processed                         | Passed            |
| **Data Transformation**  | Query `timestamp`, `event_type`, `created_at`          | Proper format and lowercased event_type              | Passed            |
| **PostgreSQL Storage**   | Count rows and check for duplicates                    | Count matches, no duplicates                         | Passed            |
| **System Robustness**    | Restart generator, delete CSV during processing        | No crashes or errors; PostgreSQL remains consistent  | Passed            |

---



###  GitHub
- Push this full project to your GitHub repository.

###  To Run:
Follow the Docker or local instructions above.



