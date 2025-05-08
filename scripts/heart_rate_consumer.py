# heart_rate_consumer.py
# Consumes heart rate data from Kafka and stores it in PostgreSQL.

import yaml
import logging
import json
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load environment variables
load_dotenv()

# Load settings from settings.yml
with open("settings.yml", "r") as file:
    settings = yaml.safe_load(file)
kafka_settings = settings["kafka"]
db_settings = settings["database"]

# Kafka and database settings
broker = kafka_settings["broker"]
topic = kafka_settings["topic"]
db_host = db_settings["host"]
db_port = db_settings["port"]
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

# Initialize Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=broker,
    group_id="heart_rate_group",
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))  # Deserialize JSON
)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = conn.cursor()

if __name__ == "__main__":
    logging.info("Starting consumer")
    try:
        for message in consumer:
            data = message.value
            # Insert into heart_rates table
            query = """
            INSERT INTO heart_rates (user_id, time, rate)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (data["user_id"], data["time"], data["rate"]))
            conn.commit()
            logging.info(f"Stored: {data}")
    except KeyboardInterrupt:
        logging.info("Stopping consumer")
        cursor.close()
        conn.close()