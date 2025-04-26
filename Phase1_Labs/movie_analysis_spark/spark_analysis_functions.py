# TMDB Movie Analysis Pipeline
# Purpose: Fetches movie data from TMDB API, cleans it, performs KPI analysis, and generates visualizations.
# This script integrates schema definition, data extraction, cleaning, analysis, and plotting for a comprehensive movie analysis.

import os
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pyspark.sql import SparkSession, Row, DataFrame
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, LongType, DoubleType, ArrayType, MapType
from pyspark.sql.functions import col, array_join, expr, size, when, to_date, mean, sum as spark_sum, count as spark_count, lit, explode, split, year
from typing import List, Optional
from dotenv import load_dotenv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt   
from pyspark import SparkConf
import os
os.environ["PYSPARK_PYTHON"] = r"C:\Users\USER\Desktop\Amasah\Amalitech\Movie_Data_Analysis\Phase1_Labs\spark_env\Scripts\python.exe"
os.environ["HADOOP_HOME"] = r"C:\hadoop"



# Configure non-interactive plotting for Matplotlib
matplotlib.use("Agg")

# Configure logging to track execution and errors
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
# Purpose: Retrieves TMDB API key securely
load_dotenv()
TMDB_API_KEY = os.getenv("API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in .env file")

# Define TMDB API endpoint and array fields
TMDB_URL = "https://api.themoviedb.org/3/movie/{id}?api_key={api}&append_to_response=credits"
JSON_ARRAY_FIELDS = ["genres", "production_companies", "production_countries", "spoken_languages"]

# Initialize Spark session with optimized settings
# Purpose: Sets up Spark for distributed data processing with sufficient memory and port configuration
spark = SparkSession.builder \
    .appName("TMDBMovieAnalysis") \
    .config("spark.driver.memory", "6g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.pyspark.python", "python") \
    .config("spark.driver.port", "4041") \
    .config("spark.blockManager.port", "7078") \
    .getOrCreate()

# Set 1: Schema Definition
def build_schema() -> StructType:
    """
    Defines the schema for TMDB movie data with nested fields for genres, credits, etc.
    Input: None
    Output: StructType schema for Spark DataFrame
    """
    # Define core movie fields (e.g., id, title, budget)
    movie_fields = [
        StructField("id", IntegerType(), False),
        StructField("title", StringType(), True),
        StructField("tagline", StringType(), True),
        StructField("release_date", StringType(), True),
        StructField("original_language", StringType(), True),
        StructField("budget", LongType(), True),
        StructField("revenue", LongType(), True),
        StructField("vote_count", IntegerType(), True),
        StructField("vote_average", DoubleType(), True),
        StructField("popularity", DoubleType(), True),
        StructField("runtime", IntegerType(), True),
        StructField("overview", StringType(), True),
        StructField("poster_path", StringType(), True),
    ]
    
    # Define collection field for franchise metadata
    collection_field = StructField("belongs_to_collection", MapType(StringType(), StringType()), True)
    
    # Helper function to create array fields (e.g., genres, production_companies)
    def create_array_field(name: str, subfields: list) -> StructField:
        return StructField(name, ArrayType(StructType(subfields)), True)
    
    # Define array fields for genres, companies, countries, languages
    array_fields = [
        create_array_field("genres", [
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
        ]),
        create_array_field("production_companies", [
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
        ]),
        create_array_field("production_countries", [
            StructField("iso_3166_1", StringType(), True),
            StructField("name", StringType(), True),
        ]),
        create_array_field("spoken_languages", [
            StructField("iso_639_1", StringType(), True),
            StructField("name", StringType(), True),
        ]),
    ]
    
    # Define credits field for cast and crew
    credits_field = StructField(
        "credits",
        StructType([
            StructField("cast", ArrayType(StructType([
                StructField("name", StringType(), True),
                StructField("character", StringType(), True),
            ])), True),
            StructField("crew", ArrayType(StructType([
                StructField("name", StringType(), True),
                StructField("job", StringType(), True),
            ])), True),
        ]),
        True,
    )
    
    return StructType(movie_fields + [collection_field] + array_fields + [credits_field])

    # ====================================================================================

#               Set 2: DATA EXTRACTION

# =========================================================================

def create_session_with_retries(retries: int = 3, delay: float = 0.5) -> requests.Session:
    """
    Creates an HTTP session with retries for reliable TMDB API calls.
    Input: retries (int), delay (float) for retry configuration
    Output: Configured requests.Session object
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=delay,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    return session

def fetch_tmdb_movies(movie_ids: List[int], schema: StructType) -> DataFrame:
    """
    Fetches movie data from TMDB API and creates a Spark DataFrame.
    Input: movie_ids (list of integers), schema (StructType)
    Output: Spark DataFrame with movie data
    """
    session = create_session_with_retries()
    movies = []
    
    for movie_id in movie_ids:
        try:
            # Fetch movie data from TMDB API
            response = session.get(TMDB_URL.format(id=movie_id, api=TMDB_API_KEY), timeout=1.0)
            response.raise_for_status()
            result = response.json()
            
            # Skip if API indicates failure
            if result.get("success", True) is False:
                logging.info(f"Skipping movie ID {movie_id}: API failure")
                continue
            
            # Extract core movie fields
            movie_data = {
                "id": int(result.get("id", 0)),  # Cast to integer
                "title": result.get("title"),
                "tagline": result.get("tagline"),
                "release_date": result.get("release_date"),
                "original_language": result.get("original_language"),
                "budget": result.get("budget"),
                "revenue": result.get("revenue"),
                "vote_count": result.get("vote_count"),
                "vote_average": result.get("vote_average"),
                "popularity": result.get("popularity"),
                "runtime": result.get("runtime"),
                "overview": result.get("overview"),
                "poster_path": result.get("poster_path"),
                "belongs_to_collection": result.get("belongs_to_collection"),
            }
            
            
            
            # Structure credits (cast and crew)
            credits = result.get("credits", {})
            movie_data["credits"] = {
                "cast": [
                    {"name": person.get("name", ""), "character": person.get("character", "")}
                    for person in credits.get("cast", [])
                ],
                "crew": [
                    {"name": person.get("name", ""), "job": person.get("job", "")}
                    for person in credits.get("crew", [])
                ]
            }
            
            movies.append(Row(**movie_data))
            logging.info(f"Fetched movie ID {movie_id}")
            
        except requests.RequestException as e:
            logging.warning(f"Failed to fetch movie ID {movie_id}: {e}")
            continue
    
    # Create DataFrame and log row count
    df = spark.createDataFrame(movies or [], schema)
    logging.info(f"Created DataFrame with {df.count()} rows")
    
    return df


# ==================================================
# Set 3: Data Cleaning
#================================================

def clean_movie_data(df: DataFrame) -> DataFrame:
    """
    Cleans and transforms raw TMDB movie data by extracting nested fields and computing metrics.
    Input: Raw Spark DataFrame
    Output: Cleaned Spark DataFrame with flattened columns and financial metrics
    """
    # Extract collection name
    cleaned_df = df.withColumn(
        "collection_name",
        col("belongs_to_collection").getItem("name")
    )
    
    # Convert array fields to pipe-separated strings
    array_fields = {
        "genre_names": "genres",
        "production_companies_str": "production_companies",
        "production_countries_str": "production_countries",
        "spoken_languages_str": "spoken_languages"
    }
    for new_col, src_col in array_fields.items():
        cleaned_df = cleaned_df.withColumn(
            new_col,
            when(col(src_col).isNotNull(),
                 array_join(expr(f"transform({src_col}, x -> x.name)"), "|"))
            .otherwise("")
        )
    
    # Extract credits: cast names, cast count, director, crew count
    cleaned_df = cleaned_df \
        .withColumn("cast_names",
                    when(col("credits").isNotNull(),
                         array_join(expr("transform(credits.cast, x -> x.name)"), "|"))
                    .otherwise("")) \
        .withColumn("cast_size", size(col("credits.cast"))) \
        .withColumn("director",
                    when(col("credits").isNotNull(),
                         array_join(expr("transform(filter(credits.crew, x -> x.job = 'Director'), x -> x.name)"), "|"))
                    .otherwise("")) \
        .withColumn("crew_size", size(col("credits.crew")))
    
    # Replace zero values with null
    cleaned_df = cleaned_df \
        .withColumn("budget", when(col("budget") == 0, None).otherwise(col("budget"))) \
        .withColumn("revenue", when(col("revenue") == 0, None).otherwise(col("revenue"))) \
        .withColumn("runtime", when(col("runtime") == 0, None).otherwise(col("runtime"))) \
        .withColumn("release_date", to_date(col("release_date")))
    
    # Compute financial metrics
    cleaned_df = cleaned_df \
        .withColumn("budget_millions", col("budget") / 1e6) \
        .withColumn("revenue_millions", col("revenue") / 1e6) \
        .withColumn("profit", col("revenue_millions") - col("budget_millions")) \
        .withColumn("roi", when(col("budget_millions") > 0, col("revenue_millions") / col("budget_millions")).otherwise(None))
    
    # Standardize specific fields
    cleaned_df = cleaned_df \
        .withColumn(
            "genre_names",
            when(col("genre_names").isin(
                "Adventure|Science Fiction|Action", "Adventure|Action|Science Fiction"),
                "Action|Adventure|Science Fiction"
            ).otherwise(col("genre_names"))
        ) \
        .withColumn(
            "production_countries_str",
            when(col("production_countries_str") == "United Kingdom|United States of America",
                 "United States of America|United Kingdom"
            ).otherwise(col("production_countries_str"))
        )
    
    # Select final columns
    selected_columns = [
        "id", "title", "tagline", "release_date", "genre_names", "collection_name",
        "original_language", "budget_millions", "revenue_millions", "production_companies_str",
        "production_countries_str", "vote_count", "vote_average", "popularity", "runtime",
        "overview", "spoken_languages_str", "poster_path", "cast_names", "cast_size",
        "director", "crew_size", "profit", "roi"
    ]
    return cleaned_df.select([col(c) for c in selected_columns if c in cleaned_df.columns])



# ==================================================
#                Set 4: KPI Analysis
#=====================================================

def kpi_ranking(df: DataFrame, metric: str, n: int = 10, top: bool = True,
                filter_col: Optional[str] = None, filter_val: Optional[float] = None) -> DataFrame:
    """
    Ranks movies by a specified metric with optional filtering.
    Input: DataFrame, metric (column name), n (number of results), top (True for top, False for bottom), filter_col, filter_val
    Output: DataFrame with ranked movies
    """
    if filter_col and filter_val is not None:
        df = df.filter(col(filter_col) >= filter_val)
    return df.orderBy(col(metric).desc() if top else col(metric).asc()).limit(n)

def advanced_search(df: DataFrame, genre: Optional[str] = None,
                   cast: Optional[str] = None, director: Optional[str] = None,
                   sort_by: Optional[str] = None, ascending: bool = True) -> DataFrame:
    """
    Filters movies by genre, cast, or director keywords and sorts results.
    Input: DataFrame, genre, cast, director (keywords), sort_by (column), ascending (sort direction)
    Output: Filtered and sorted DataFrame
    """
    filters = {
        "genre_names": genre,
        "cast_names": cast,
        "director": director
    }
    for col_name, keyword in filters.items():
        if keyword:
            df = df.filter(col(col_name).contains(keyword))
    return df.orderBy(col(sort_by).asc() if ascending else col(sort_by).desc()) if sort_by else df

def franchise_vs_standalone(df: DataFrame) -> DataFrame:
    """
    Compares franchise and standalone movies on key metrics.
    Input: Cleaned DataFrame
    Output: DataFrame with average metrics for franchise and standalone groups
    """
    def summarize(group: DataFrame, label: str) -> DataFrame:
        return group.agg(
            mean("revenue_millions").alias("Mean_Revenue"),
            mean("roi").alias("Mean_ROI"),
            mean("budget_millions").alias("Mean_Budget"),
            mean("popularity").alias("Mean_Popularity"),
            mean("vote_average").alias("Mean_Rating"),
            spark_count("*").alias("Movie_Count")
        ).withColumn("Group", lit(label))
    
    return summarize(df.filter(col("collection_name").isNotNull()), "Franchise") \
        .union(summarize(df.filter(col("collection_name").isNull()), "Standalone"))

def analyze_franchise(df: DataFrame, sort_by: Optional[str] = None, ascending: bool = False) -> DataFrame:
    """
    Aggregates metrics for franchises.
    Input: DataFrame, sort_by (metric), ascending (sort direction)
    Output: DataFrame with franchise-level metrics
    """
    stats = df.filter(col("collection_name").isNotNull()) \
        .groupBy("collection_name").agg(
            spark_count("id").alias("Total_Movies"),
            spark_sum("revenue_millions").alias("Total_Revenue"),
            mean("revenue_millions").alias("Avg_Revenue"),
            mean("vote_average").alias("Avg_Rating"),
            mean("roi").alias("Avg_ROI")
        )
    return stats.orderBy(col(sort_by).asc() if ascending else col(sort_by).desc()) if sort_by else stats

def analyze_directors(df: DataFrame, sort_by: Optional[str] = None, ascending: bool = False) -> DataFrame:
    """
    Analyzes directors' performance in franchise movies.
    Input: DataFrame, sort_by (metric), ascending (sort direction)
    Output: DataFrame with director-level metrics
    """
    directors_df = df.filter(col("collection_name").isNotNull()) \
        .withColumn("director", explode(split(col("director"), "\\|"))) \
        .filter(col("director") != "")
    
    stats = directors_df.groupBy("director").agg(
        spark_count("id").alias("Total_Movies"),
        spark_sum("revenue_millions").alias("Total_Revenue"),
        mean("revenue_millions").alias("Avg_Revenue"),
        mean("vote_average").alias("Avg_Rating"),
        mean("roi").alias("Avg_ROI")
    )
    return stats.orderBy(col(sort_by).asc() if ascending else col(sort_by).desc()) if sort_by else stats



# =====================================================
#         Set 5: Visualization
#=======================================================
def plot_revenue_vs_budget(df: DataFrame) -> None:
    """
    Creates a scatter plot of movie budgets vs. revenues.
    Input: DataFrame with 'budget_millions' and 'revenue_millions' columns
    Output: Saves 'revenue_vs_budget.png' plot
    """
    # Select and convert data to Pandas
    pdf = df.select("budget_millions", "revenue_millions").dropna().toPandas()
    if pdf.empty:
        logging.warning("No data for revenue vs. budget plot")
        return
    
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(pdf["budget_millions"], pdf["revenue_millions"], alpha=0.5, color="blue")
    plt.title("Budget vs. Revenue")
    plt.xlabel("Budget (Millions USD)")
    plt.ylabel("Revenue (Millions USD)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("revenue_vs_budget.png")
    plt.close()

def plot_roi_by_genre(df: DataFrame) -> None:
    """
    Creates a bar chart of average ROI by genre.
    Input: DataFrame with 'roi' and 'genre_names' columns
    Output: Saves 'roi_by_genre.png' plot
    """
    # Explode genres and filter non-null ROI
    df_genres = df.select("roi", explode(split(col("genre_names"), "\\|")).alias("genre")) \
                  .filter(col("roi").isNotNull())
    genre_roi = df_genres.groupBy("genre").agg(mean("roi").alias("avg_roi")) \
                         .orderBy(col("avg_roi").desc()).toPandas()
    
    if genre_roi.empty:
        logging.warning("No data for ROI by genre plot")
        return
    
    # Create bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(genre_roi["genre"], genre_roi["avg_roi"], color="lightgreen")
    plt.title("Average ROI by Genre")
    plt.xlabel("Genre")
    plt.ylabel("Average ROI")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("roi_by_genre.png")
    plt.close()

def plot_popularity_vs_rating(df: DataFrame) -> None:
    """
    Creates a scatter plot of popularity vs. average rating.
    Input: DataFrame with 'popularity' and 'vote_average' columns
    Output: Saves 'popularity_vs_rating.png' plot
    """
    # Select and convert data to Pandas
    pdf = df.select("popularity", "vote_average").dropna().toPandas()
    if pdf.empty:
        logging.warning("No data for popularity vs. rating plot")
        return
    
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(pdf["popularity"], pdf["vote_average"], alpha=0.5, color="purple")
    plt.title("Popularity vs. Rating")
    plt.xlabel("Popularity Score")
    plt.ylabel("Average Rating")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("popularity_vs_rating.png")
    plt.close()

def plot_yearly_box_office(df: DataFrame) -> None:
    """
    Creates a line plot of total box office revenue by year.
    Input: DataFrame with 'release_date' and 'revenue_millions' columns
    Output: Saves 'yearly_box_office.png' plot
    """
    # Extract year and filter non-null revenue
    df_year = df.withColumn("year", year(to_date(col("release_date")))) \
                .filter(col("revenue_millions").isNotNull() & col("year").isNotNull())
    yearly_revenue = df_year.groupBy("year") \
                            .agg(spark_sum("revenue_millions").alias("total_revenue")) \
                            .orderBy("year").toPandas()
    
    if yearly_revenue.empty:
        logging.warning("No data for yearly box office plot")
        return
    
    # Create line plot
    plt.figure(figsize=(12, 6))
    plt.plot(yearly_revenue["year"], yearly_revenue["total_revenue"], marker="o", color="orange")
    plt.title("Annual Box Office Revenue")
    plt.xlabel("Year")
    plt.ylabel("Total Revenue (Millions USD)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("yearly_box_office.png")
    plt.close()

def plot_franchise_vs_standalone(df: DataFrame) -> None:
    """
    Creates a bar chart comparing franchise vs. standalone movie metrics.
    Input: DataFrame with 'collection_name', 'revenue_millions', 'budget_millions', 'vote_average' columns
    Output: Saves 'franchise_vs_standalone.png' plot
    """
    # Compute metrics for franchise and standalone movies
    def compute_metrics(sub_df: DataFrame) -> list:
        stats = sub_df.agg(
            mean("revenue_millions").alias("revenue"),
            mean("budget_millions").alias("budget"),
            mean("vote_average").alias("rating")
        ).collect()[0]
        return [stats["revenue"], stats["budget"], stats["rating"]]
    
    franchise_metrics = compute_metrics(df.filter(col("collection_name").isNotNull()))
    standalone_metrics = compute_metrics(df.filter(col("collection_name").isNull()))
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame({
        "Franchise": franchise_metrics,
        "Standalone": standalone_metrics
    }, index=["Average Revenue", "Average Budget", "Average Rating"])
    
    # Create bar chart
    comparison_df.plot(kind="bar", figsize=(10, 6), color=["#1f77b4", "#ff7f0e"])
    plt.title("Franchise vs. Standalone Movies")
    plt.xlabel("Metric")
    plt.ylabel("Value")
    plt.xticks(rotation=0)
    plt.legend(title="Movie Type")
    plt.tight_layout()
    plt.savefig("franchise_vs_standalone.png")
    
    plt.close()

#==========================================
# Main Execution
#===================================

def main():
    """
    Runs the TMDB movie analysis pipeline: fetches data, cleans it, performs analysis, and generates visualizations.
    Input: None
    Output: Displays DataFrames, saves analysis results, and generates plot files
    """
    # Define movie IDs to fetch
    movie_ids = [
        299534, 19995, 140607, 299536, 597, 135397,
        420818, 24428, 168259, 99861, 284054, 12445,
        181808, 330457, 351286, 109445, 321612, 260513
    ]
    
    logging.info("Starting TMDB movie analysis")
    
    # Fetch data
    schema = build_schema()
    logging.info("Schema defined")
    raw_df = fetch_tmdb_movies(movie_ids, schema)
    
    # Validate raw DataFrame
    if raw_df.count() == 0:
        logging.error("No data fetched. Check API key or movie IDs.")
        return
    
    # Display raw DataFrame schema and sample
    logging.info("Raw DataFrame schema:")
    raw_df.printSchema()
    logging.info("Sample Raw Data:")
    #raw_df.show(5, truncate=False)
    
    # Clean data
    cleaned_df = clean_movie_data(raw_df)
    
    # Validate cleaned DataFrame
    if cleaned_df.count() == 0:
        logging.error("No data after cleaning. Check data processing steps.")
        return
    
    # Display cleaned DataFrame schema and sample
    logging.info("Cleaned DataFrame schema:")
    cleaned_df.printSchema()
    logging.info("Sample Cleaned Data:")
    cleaned_df.show(5, truncate=False)
    
    # Perform analysis
    logging.info("Top 5 Movies by Revenue:")
    kpi_ranking(cleaned_df, "revenue_millions", n=5).select(
        "title", "revenue_millions", "budget_millions"
    ).show(truncate=False)
    
    logging.info("Movies with Action Genre:")
    advanced_search(cleaned_df, genre="Action", sort_by="revenue_millions").select(
        "title", "genre_names", "revenue_millions"
    ).show(truncate=False)
    
    logging.info("Franchise vs Standalone Comparison:")
    franchise_vs_standalone(cleaned_df).show(truncate=False)
    
    logging.info("Top Franchises by Total Revenue:")
    analyze_franchise(cleaned_df, sort_by="Total_Revenue").show(5, truncate=False)
    
    logging.info("Top Directors by Total Revenue:")
    analyze_directors(cleaned_df, sort_by="Total_Revenue").show(5, truncate=False)
    
    # Generate all visualizations
    logging.info("Generating visualizations...")
    plot_revenue_vs_budget(cleaned_df)
    logging.info("Saved revenue_vs_budget.png")
    
    plot_roi_by_genre(cleaned_df)
    logging.info("Saved roi_by_genre.png")
    
    plot_popularity_vs_rating(cleaned_df)
    logging.info("Saved popularity_vs_rating.png")
    
    plot_yearly_box_office(cleaned_df)
    logging.info("Saved yearly_box_office.png")
    
    plot_franchise_vs_standalone(cleaned_df)
    logging.info("Saved franchise_vs_standalone.png")

if __name__ == "__main__":
    try:
        main()
        logging.info("Analysis complete!")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise
    finally:
        # Clean up Spark session
        spark.stop()
        logging.info("Spark session stopped")