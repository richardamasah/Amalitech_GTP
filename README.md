#  Real-Time Heart Rate Streaming Pipeline

This project is a **Dockerized real-time data pipeline** that simulates heart rate data from wearable devices, streams it through **Apache Kafka**, stores it in **PostgreSQL**, and visualizes the data with **Grafana**. It also includes **pgAdmin** for managing the database.

The pipeline is built for scalability, observability, and hands-on learning in data engineering and real-time analytics.

---

##  Project Overview

**Key features**:
-  **Data Generation**: Simulates heart rate data for 500 users with realistic and outlier values.
-  **Streaming**: Kafka enables fast, fault-tolerant real-time message delivery.
-  **Storage**: PostgreSQL stores heart rate data with indexing for performance.
-  **Visualization**: Grafana dashboards visualize trends and anomalies.
-  **Management**: pgAdmin for querying and DB schema management.

---

##  Components

| File/Service               | Purpose                                               |
|---------------------------|-------------------------------------------------------|
| `producer.py`             | Generates and publishes heart rate data to Kafka     |
| `consumer.py`             | Consumes Kafka data and stores in PostgreSQL         |
| `create_table.sql`        | PostgreSQL schema for `heart_rate_data` table        |
| `Dockerfile`              | Python image with dependencies                       |
| `docker-compose.yml`      | Orchestrates all services (Kafka, ZK, PG, etc.)      |
| `requirements.txt`        | Python dependencies                                   |
| Grafana                   | http://localhost:3000 - visualizes heart rate data   |
| pgAdmin                   | http://localhost:5050 - PostgreSQL management UI     |

---

##  Prerequisites

- Docker & Docker Compose installed
- Free ports: `2181`, `9092`, `5433`, `3000`, `5050`
- ~2GB disk space for images

---

##  Project Structure

```

heart\_rate\_streaming/
├── producer.py
├── consumer.py
├── create\_table.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md

````

---

##  Setup Instructions

### 1. Clone the Repo
```bash
git clone <your-repo-url>
cd heart_rate_streaming
````

### 2. Start All Services

```bash
docker-compose up --build
```

**Services launched**:

* Kafka + Zookeeper
* PostgreSQL (port `5433`)
* Producer & Consumer
* Grafana (port `3000`)
* pgAdmin (port `5050`)

---

##  Verification

### Check logs:

```bash
docker-compose logs producer
docker-compose logs consumer
```

You should see:

* Producer: `Sending to Kafka: {...}`
* Consumer: `Stored data: {...}`

---

##  pgAdmin (DB Access)

1. Go to [http://localhost:5050](http://localhost:5050)

2. Login:

   * Email: `admin@admin.com`
   * Password: `password`

3. Add server:

   * Name: `postgres`
   * Host: `postgres`
   * Port: `5432`
   * DB: `heart_rate_db`
   * User: `admin`
   * Password: `password`

---

##  Grafana (Visualization)

1. Open [http://localhost:3000](http://localhost:3000)

   * Login: `admin / admin`

2. Add PostgreSQL data source:

   * Host: `postgres:5432`
   * DB: `heart_rate_db`
   * User: `admin`
   * Password: `password`

3. Create dashboard:

   * **Query**:

     ```sql
     SELECT timestamp, heart_rate FROM heart_rate_data WHERE customer_id = $customer_id
     ```

4. Add `$customer_id` as a variable:

   * Query: `SELECT DISTINCT customer_id FROM heart_rate_data`

---

##  Stopping the Pipeline

```bash
docker-compose down
# or clean everything
docker-compose down -v
```

---

##  Troubleshooting

###  No data in database?

* Check `docker-compose logs consumer`
* Make sure PostgreSQL is healthy and the topic exists

###  Kafka connection errors?

* Ensure `kafka:9092` is up
* Validate topic name in both producer and consumer

###  Timestamp issues?

* Ensure `consumer.py` converts ISO to datetime:

  ```python
  from datetime import datetime
  data['timestamp'] = datetime.fromisoformat(data['timestamp'])
  ```

---

##  Development Info

* **Python**: 3.9+
* **Kafka Python Client**: `confluent-kafka`
* **PostgreSQL**: via official `postgres:15` image
* **Visualization**: Grafana
* **Schema**: Enforces data range for heart rate, age, and weight

---

##  Extending the Project

* Add anomaly detection (e.g., flag `heart_rate > 100`)
* Trigger alerts via Grafana thresholds
* Stream enriched data to another Kafka topic

---

##  Contributing

1. Fork the repo
2. Create a feature branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit & push:

   ```bash
   git commit -m "Add feature"
   git push origin feature-name
   ```
4. Open a pull request

---

##  License

MIT License — See `LICENSE` file (if added)

---

##  Acknowledgments

* Built using open-source tools: **Kafka**, **PostgreSQL**, **Grafana**, **pgAdmin**
* Inspired by modern real-time data systems

```
