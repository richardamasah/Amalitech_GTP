# src/data_generator.py
# Generates fake e-commerce events (view, purchase) and saves them as CSV files in data/.
# Purpose: Simulates user actions for the Spark streaming pipeline to process.

import os
import csv
import time
import random
from datetime import datetime
from faker import Faker

# Initialize Faker for realistic fake data (e.g., UUIDs)

fake = Faker()

# Define possible actions and products as constants

ACTIONS = ["view", "purchase"]
PRODUCTS = [
    {"id": "prod1", "name": "Laptop", "category": "Electronics", "price": 999.99},
    {"id": "prod2", "name": "Smartphone", "category": "Electronics", "price": 699.99},
    {"id": "prod3", "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"id": "prod4", "name": "T-shirt", "category": "Clothing", "price": 19.99},
    {"id": "prod5", "name": "Sneakers", "category": "Footwear", "price": 79.99},
]

def generate_event():
    """
    Generate a single e-commerce event with fields required by the Spark pipeline.
    Returns: Dictionary with event details (event_id, user_id, action, etc.).
    
    """
    product = random.choice(PRODUCTS)
    return {
        "event_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "action": random.choice(ACTIONS),
        "product_id": product["id"],
        "product_name": product["name"],
        "category": product["category"],
        "price": product["price"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def save_event_to_csv(event, output_dir="data"):
    """
    Save a single event to a CSV file with a timestamped filename.
    Args:
        event: Dictionary containing event data.
        output_dir: Directory to save CSV files (default: data/).
    Returns: Path to the saved CSV file.
    
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(output_dir, f"event_{timestamp}.csv")
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=event.keys())
        writer.writeheader()
        writer.writerow(event)
    return filename

def main():
    """
    Main function to continuously generate and save e-commerce events.
    Runs indefinitely, generating one event every 5 seconds.
    
    """
    print("Starting data generator...")
    try:
        while True:
            event = generate_event()
            filename = save_event_to_csv(event)
            print(f"Generated event: {event['event_id']} saved to {filename}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping data generator.")

if __name__ == "__main__":
    main()