# heart_rate_producer.py
# Publishes heart rate data to a Kafka topic.

import yaml
import logging
import json
import time
from kafka import KafkaProducer
from heart_rate_generator import create_heart_rate

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Load settings from settings.yml
with open("settings.yml", "r") as file:
    settings = yaml.safe_load(file)
kafka_settings = settings["kafka"]
broker = kafka_settings["broker"]  # Kafka broker address
topic = kafka_settings["topic"]   # Kafka topic name

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=broker,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")  # Serialize to JSON
)

if __name__ == "__main__":
    logging.info(f"Starting producer for topic: {topic}")
    try:
        while True:
            # Generate heart rate data
            data = create_heart_rate()
            # Send to Kafka topic
            producer.send(topic, value=data)
            logging.info(f"Sent: {data}")
            producer.flush()  # Ensure immediate send
            time.sleep(2)     # Send every 2 seconds
    except KeyboardInterrupt:
        logging.info("Stopping producer")
        producer.close()