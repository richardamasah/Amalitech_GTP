## Project Overview   

This project builds a real-time data pipeline to simulate and process e-commerce user activity using Spark Structured Streaming and PostgreSQL.
System Components

Data Generator: data_generator.py creates CSV files with fake user events (views, purchases) in data/events/. 

Spark Streaming: spark_streaming_to_postgres.py monitors CSVs, transforms data (e.g., timestamp conversion), and writes to PostgreSQL.
PostgreSQL: Stores events in the user_events table in the ecommerce_events database, set up by postgres_setup.sql.
Connection Details: postgres_connection_details.txt contains database access info (host, port, user, password).

## Data Flow

CSVs with fake events are generated every 5 seconds.
Spark Structured Streaming reads new CSVs in real time.
Data is transformed (e.g., timestamp to TIMESTAMP, event_type to lowercase).
Processed data is appended to the user_events table in PostgreSQL.
Performance metrics are monitored via Spark UI.

## Architecture
See System_architecture.png for the pipeline diagram: Data Generator → CSV Files → Spark Streaming → PostgreSQL.
