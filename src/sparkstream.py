# src/sparkstream.py
# Spark Structured Streaming job to read e-commerce events from CSV files,
# process them, and store in PostgreSQL with error handling and env variables.

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define CSV schema
schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("action", StringType(), False),
    StructField("product_id", StringType(), False),
    StructField("product_name", StringType(), False),
    StructField("category", StringType(), False),
    StructField("price", FloatType(), False),
    StructField("timestamp", StringType(), False),
])

def create_spark_session():
    """Create Spark session with error handling."""
    try:
        spark = (SparkSession.builder
                 .appName("EcommerceStreaming")
                 .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
                 .getOrCreate())
        logging.info("Spark session created successfully")
        return spark
    except Exception as e:
        logging.error(f"Failed to create Spark session: {e}")
        raise

def process_stream(spark, input_dir, checkpoint_dir, db_url, db_user, db_password):
    """Read CSVs, process, and write to PostgreSQL with error handling."""
    try:
        df = (spark.readStream
              .schema(schema)
              .csv(input_dir)
              .withColumn("timestamp", col("timestamp").cast(TimestampType())))
        logging.info(f"Reading CSVs from {input_dir}")

        df = df.filter(col("price") >= 0)
        df = df.dropDuplicates(["event_id"])
        logging.info("Applied transformations: price filter, deduplication")

        def write_to_postgres(batch_df, batch_id):
            try:
                batch_df.write \
                    .format("jdbc") \
                    .option("url", db_url) \
                    .option("dbtable", "ecommerce_events") \
                    .option("user", db_user) \
                    .option("password", db_password) \
                    .option("driver", "org.postgresql.Driver") \
                    .mode("append") \
                    .save()
                logging.info(f"Batch {batch_id} written to PostgreSQL")
            except Exception as e:
                logging.error(f"Failed to write batch {batch_id} to PostgreSQL: {e}")

        query = (df.writeStream
                 .foreachBatch(write_to_postgres)
                 .option("checkpointLocation", checkpoint_dir)
                 .start())
        logging.info("Streaming query started")
        return query
    except Exception as e:
        logging.error(f"Streaming process failed: {e}")
        raise

def main():
    """Main function to run Spark streaming with error handling."""
    try:
        spark = create_spark_session()
        db_url = f"jdbc:postgresql://postgres:5432/{os.getenv('DB_NAME')}"
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        input_dir = "/app/data"
        checkpoint_dir = "/app/checkpoint"
        query = process_stream(spark, input_dir, checkpoint_dir, db_url, db_user, db_password)
        query.awaitTermination()
    except Exception as e:
        logging.error(f"Streaming job failed: {e}")
        raise

if __name__ == "__main__":
    main()