import os
import time
from datetime import datetime
from faker import Faker
import pandas as pd


def initialize_faker():
    """Initialize and return a Faker instance for generating fake data.

    Returns:
        Faker: An instance of the Faker class.
    """
    return Faker()


def generate_event(fake: Faker) -> dict:
    """Generate a single fake e-commerce event.

    Args:
        fake (Faker): An instance of the Faker class for generating fake data.

    Returns:
        dict: A dictionary containing event details (event_id, user_id, etc.).
    """
    return {
        "event_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "event_type": fake.random_element(elements=("view", "purchase")),
        "product_id": fake.uuid4(),
        "product_name": fake.word().capitalize() + " " + fake.word().capitalize(),
        "price": round(fake.random_number(digits=4) / 100, 2),
        "timestamp": fake.date_time_this_year().isoformat()
    }


def save_events_to_csv(events: list, output_dir: str) -> str:
    """Save a list of events to a CSV file with a timestamped filename.

    Args:
        events (list): List of event dictionaries to save.
        output_dir (str): Directory where the CSV file will be saved.

    Returns:
        str: Path to the saved CSV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    df = pd.DataFrame(events)
    timestamp = int(datetime.now().timestamp())
    file_path = os.path.join(output_dir, f"events_{timestamp}.csv")
    df.to_csv(file_path, index=False)
    return file_path


def generate_and_save_batch(fake: Faker, num_events: int, output_dir: str) -> str:
    """Generate a batch of events and save them to a CSV file.

    Args:
        fake (Faker): An instance of the Faker class.
        num_events (int): Number of events to generate in the batch.
        output_dir (str): Directory where the CSV file will be saved.

    Returns:
        str: Path to the saved CSV file.
    """
    events = [generate_event(fake) for _ in range(num_events)]
    return save_events_to_csv(events, output_dir)


def main(output_dir: str = "./data", num_events: int = 10, interval: int = 5):
    """Run the data generator to continuously produce event CSVs.

    Args:
        output_dir (str, optional): Directory to save CSV files. Defaults to "../data/events".
        num_events (int, optional): Number of events per batch. Defaults to 10.
        interval (int, optional): Seconds to wait between batches. Defaults to 5.
    """
    fake = initialize_faker()
    print(f"Starting data generator. Saving CSVs to {os.path.abspath(output_dir)}")
    
    try:
        while True:
            file_path = generate_and_save_batch(fake, num_events, output_dir)
            print(f"Saved {file_path}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Data generator stopped.")


if __name__ == "__main__":
    main()