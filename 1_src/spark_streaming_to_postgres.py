from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
import pyspark.sql.functions as F


def initialize_spark() -> SparkSession:
    """Initialize and return a SparkSession for Structured Streaming.

    Returns:
        SparkSession: Configured Spark session.
    """
    return SparkSession.builder \
        .appName("EcommerceStreaming") \
        .config("spark.jars", "/path/to/postgresql-42.6.0.jar") \
        .getOrCreate()


def define_schema() -> StructType:
    """Define the schema for the CSV files.

    Returns:
        StructType: Schema matching the CSV structure.
    """
    return StructType([
        StructField("event_id", StringType(), False),
        StructField("user_id", StringType(), False),
        StructField("event_type", StringType(), False),
        StructField("product_id", StringType(), False),
        StructField("product_name", StringType(), True),
        StructField("price", FloatType(), True),
        StructField("timestamp", StringType(), False)
    ])


def read_stream(spark: SparkSession, schema: StructType, input_path: str):
    """Read CSV files as a streaming DataFrame.

    Args:
        spark (SparkSession): Spark session.
        schema (StructType): Schema for the CSV files.
        input_path (str): Path to the folder containing CSVs.

    Returns:
        DataFrame: Streaming DataFrame from CSV files.
    """
    return spark.readStream \
        .schema(schema) \
        .csv(input_path)


def transform_stream(df):
    """Apply transformations to the streaming DataFrame.

    Args:
        df (DataFrame): Input streaming DataFrame.

    Returns:
        DataFrame: Transformed streaming DataFrame.
    """
    # Convert timestamp string to TIMESTAMP type
    # Clean event_type by trimming and converting to lowercase
    # Add created_at as current timestamp
    return df.withColumn("timestamp", F.to_timestamp("timestamp")) \
            .withColumn("event_type", F.lower(F.trim("event_type"))) \
            .withColumn("created_at", F.current_timestamp())


def write_to_postgres(batch_df, batch_id):
    """Write a batch of streaming data to PostgreSQL.

    Args:
        batch_df (DataFrame): Micro-batch DataFrame to write.
        batch_id (int): ID of the micro-batch.
    """
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/ecommerce_events") \
        .option("dbtable", "user_events") \
        .option("user", "postgres") \
        .option("password", "mysecretpassword") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()


def main(input_path: str = "../data/events"):
    """Run the Spark Structured Streaming job to process CSVs and write to PostgreSQL.

    Args:
        input_path (str, optional): Path to CSV folder. Defaults to "../data/events".
    """
    spark = initialize_spark()
    schema = define_schema()
    df = read_stream(spark, schema, input_path)
    df_transformed = transform_stream(df)

    # Write stream to PostgreSQL
    query = df_transformed.writeStream \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    main()