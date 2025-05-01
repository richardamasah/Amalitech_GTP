## User Guide  
------------------------------------------------------------------------------------

This guide provides step-by-step instructions to set up and run the real-time e-commerce data pipeline using Spark Structured Streaming and PostgreSQL.
Prerequisites
--------------------------------------------------------------------------------------------
# Software:  
Python 3.8+
PostgreSQL 13+
Apache Spark 3.4.0+ (with Hadoop)
Java 8 or 11


# Python Packages:  
Install via pip: faker, pandas, pyspark


PostgreSQL JDBC Driver:
Download postgresql-42.6.0.jar from jdbc.postgresql.org and place in $SPARK_HOME/jars.



## Setup

Create Virtual Environment:python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install faker pandas pyspark


Configure Spark:export SPARK_HOME=~/spark
export PATH=$SPARK_HOME/bin:$PATH
export PYSPARK_PYTHON=python3


Set Up PostgreSQL:
Start PostgreSQL server.
Create database:psql -U postgres -c "CREATE DATABASE ecommerce_events;"


Run table setup:psql -U postgres -d ecommerce_events -f scripts/postgres_setup.sql




Update Spark Script:
In scripts/spark_streaming_to_postgres.py, replace:
/path/to/postgresql-42.6.0.jar with the actual JDBC driver path.
your_password with your PostgreSQL password.





Running the Project

Start Data Generator:
In a terminal, navigate to ecommerce-streaming/scripts/ and run:python data_generator.py


This generates CSVs in data/events/ every 5 seconds.


Run Spark Streaming:
In a new terminal, activate the virtual environment and run:spark-submit scripts/spark_streaming_to_postgres.py


This processes CSVs and writes to PostgreSQL.



Verification

Check CSVs:
Verify CSV files in data/events/ (e.g., events_174xxxxxx.csv).


Check PostgreSQL:
Connect to the database:psql -U postgres -d ecommerce_events


Query:SELECT * FROM user_events LIMIT 10;


Expected: Rows with event data (e.g., event_id, user_id, timestamp).


Monitor Spark:
Open Spark UI at http://localhost:4040 to check streaming progress.



Stopping the Project

Stop data_generator.py and spark_streaming_to_postgres.py with Ctrl+C.
Shut down PostgreSQL if needed.

