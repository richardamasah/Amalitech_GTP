# heart_rate_generator.py
# Generates synthetic heart rate data for streaming.

import random
from faker import Faker
from datetime import datetime

# Initialize Faker for fake customer names
fake = Faker()

# Create 500 unique customer IDs
CUSTOMER_IDS = [f"user_{fake.user_name()}_{str(i).zfill(3)}" for i in range(500)]

def create_heart_rate():
    """
    Creates a single heart rate record.
    Returns a dictionary with user_id, time, and rate.
    """
    # Random customer ID
    user_id = random.choice(CUSTOMER_IDS)
    # Current UTC time in ISO format
    time = datetime.utcnow().isoformat() + "Z"
    # Heart rate: 80% normal (60-90), 20% outliers (50-59 or 91-110)
    rate = random.randint(60, 90) if random.random() < 0.8 else random.choice(
        [random.randint(50, 59), random.randint(91, 110)]
    )
    
    return {
        "user_id": user_id,
        "time": time,
        "rate": rate
    }