import pandas as pd
import numpy as np
import requests
import json
import os
import time
from dotenv import load_dotenv
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file")

# Movie IDs from project requirements
MOVIE_IDS = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513
]

# ===============================
# Session 1: Data Fetching
# ===============================
def fetch_movie_data(movie_ids: List[int], api_key: str) -> pd.DataFrame:
    """
    Fetches movie data from TMDB API with simple retry logic.
    
    Args:
        movie_ids: List of TMDB movie IDs
        api_key: TMDB API key
    
    Returns:
        DataFrame containing movie data
    """
    base_url = "https://api.themoviedb.org/3/movie/{}"
    params = {"api_key": api_key, "append_to_response": "credits"}
    all_data = []
    max_retries = 3
    
    for movie_id in movie_ids:
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url.format(movie_id), params=params)
                response.raise_for_status()
                all_data.append(response.json())
                break  # Success, move to next movie
            except requests.exceptions.RequestException as e:
                if attempt + 1 == max_retries:
                    logger.error(f"Failed to fetch Movie ID {movie_id} after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        time.sleep(0.1)  # Rate limiting
    
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# ===============================
# Session 2: Data Cleaning
# ===============================
def clean_json_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes JSON-like columns into clean formats.
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with cleaned JSON columns
    """
    def extract_collection(x):
        return x['name'] if isinstance(x, dict) and 'name' in x else np.nan
    
    def extract_list(x, key: str = 'name'):
        if isinstance(x, list):
            return "|".join([item[key] for item in x if key in item])
        return np.nan
    
    df = df.copy()
    df['belongs_to_collection'] = df['belongs_to_collection'].apply(extract_collection)
    df['genres'] = df['genres'].apply(lambda x: extract_list(x))
    df['production_countries'] = df['production_countries'].apply(lambda x: extract_list(x))
    df['spoken_languages'] = df['spoken_languages'].apply(
        lambda x: extract_list(x, key='english_name')
    )
    df['production_companies'] = df['production_companies'].apply(lambda x: extract_list(x))
    
    return df

def clean_basic_movie_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs basic data cleaning and preprocessing.
    
    Args:
        df: Raw movie DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()
    
    # Drop irrelevant columns
    to_drop = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    df.drop(columns=[col for col in to_drop if col in df.columns], inplace=True)
    
    # Clean JSON columns
    df = clean_json_columns(df)
    
    # Convert data types
    numeric_cols = ['id', 'budget', 'popularity', 'revenue', 'runtime']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # Handle unrealistic values
    df[['budget', 'revenue', 'runtime']] = df[['budget', 'revenue', 'runtime']].replace(0, np.nan)
    df['budget_musd'] = df['budget'] / 1_000_000
    df['revenue_musd'] = df['revenue'] / 1_000_000
    
    # Clean vote data
    df.loc[(df['vote_count'] == 0) & (df['vote_average'] > 0), 'vote_average'] = np.nan
    
    # Clean text columns
    for col in ['overview', 'tagline']:
        df[col] = df[col].replace(['No Data', 'null', '', 'None'], np.nan)
    
    # Remove invalid rows
    df = df.drop_duplicates(subset='id')
    df = df.dropna(subset=['id', 'title'])
    df = df[df.notna().sum(axis=1) >= 10]
    df = df[df['status'] == 'Released'].drop(columns='status')
    
    # Reorder columns
    desired_columns = [
        'id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
        'original_language', 'budget_musd', 'revenue_musd', 'production_companies',
        'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime',
        'overview', 'spoken_languages', 'poster_path'
    ]
    df = df[[col for col in desired_columns if col in df.columns]]
    
    return df.reset_index(drop=True)

# ===============================
# Session 3: Credits Extraction
# ===============================
def extract_credits_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts cast, crew, and director info from credits column.
    
    Args:
        df: DataFrame with credits column
    
    Returns:
        DataFrame with new credit-related columns
    """
    df = df.copy()
    
    def parse_credits(x):
        try:
            return x if isinstance(x, dict) else json.loads(x)
        except Exception:
            return {}
    
    df['credits_parsed'] = df['credits'].apply(parse_credits)
    
    def get_main_cast(credit):
        try:
            cast = credit.get('cast', [])[:3]
            return ", ".join([actor['name'] for actor in cast])
        except:
            return np.nan
    
    def get_cast_size(credit):
        return len(credit.get('cast', [])) if isinstance(credit, dict) else np.nan
    
    def get_crew_size(credit):
        return len(credit.get('crew', [])) if isinstance(credit, dict) else np.nan
    
    def get_director(credit):
        try:
            for person in credit.get('crew', []):
                if person.get('job') == 'Director':
                    return person.get('name')
            return np.nan
        except:
            return np.nan
    
    df['main_cast'] = df['credits_parsed'].apply(get_main_cast)
    df['cast_size'] = df['credits_parsed'].apply(get_cast_size)
    df['crew_size'] = df['credits_parsed'].apply(get_crew_size)
    df['director'] = df['credits_parsed'].apply(get_director)
    
    return df.drop(columns=['credits', 'credits_parsed'])

# ===============================
# Session 4: KPI Analysis
# ===============================
def calculate_kpis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Calculates and ranks movies based on key performance indicators (KPIs).
    
    Args:
        df: Cleaned movie DataFrame
    
    Returns:
        Dictionary of ranked DataFrames for each KPI
    """
    df = df.copy()
    df['profit_musd'] = df['revenue_musd'] - df['budget_musd']
    df['roi'] = df['revenue_musd'] / df['budget_musd']
    
    roi_df = df[df['budget_musd'] >= 10]
    rated_df = df[df['vote_count'] >= 10]
    
    def top_n(data: pd.DataFrame, column: str, ascending: bool = False, n: int = 5) -> pd.DataFrame:
        return data[['id', 'title', column]].sort_values(by=column, ascending=ascending).head(n)
    
    return {
        'highest_revenue': top_n(df, 'revenue_musd'),
        'highest_budget': top_n(df, 'budget_musd'),
        'highest_profit': top_n(df, 'profit_musd'),
        'lowest_profit': top_n(df, 'profit_musd', ascending=True),
        'highest_roi': top_n(roi_df, 'roi'),
        'lowest_roi': top_n(roi_df, 'roi', ascending=True),
        'most_voted': top_n(df, 'vote_count'),
        'highest_rated': top_n(rated_df, 'vote_average'),
        'lowest_rated': top_n(rated_df, 'vote_average', ascending=True),
        'most_popular': top_n(df, 'popularity')
    }

# ===============================
# Session 5: Advanced Filtering
# ===============================
def filter_movies(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Performs advanced filtering for specific movie queries.
    
    Args:
        df: Cleaned movie DataFrame
    
    Returns:
        Dictionary of filtered DataFrames
    """
    df = df.copy()
    
    # Search 1: Sci-Fi Action movies with Bruce Willis
    sci_fi_action = df[
        df['genres'].str.contains('Science Fiction', na=False) &
        df['genres'].str.contains('Action', na=False) &
        df['main_cast'].str.contains('Bruce Willis', na=False)
    ].sort_values('vote_average', ascending=False)[['id', 'title', 'vote_average']]
    
    # Search 2: Uma Thurman movies directed by Quentin Tarantino
    thurman_tarantino = df[
        df['main_cast'].str.contains('Uma Thurman', na=False) &
        (df['director'] == 'Quentin Tarantino')
    ].sort_values('runtime')[['id', 'title', 'runtime']]
    
    return {
        'sci_fi_action_willis': sci_fi_action,
        'thurman_tarantino': thurman_tarantino
    }

# ===============================
# Session 6: Franchise and Director Analysis
# ===============================
def compare_franchises(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compares franchise vs standalone movie performance.
    
    Args:
        df: Cleaned movie DataFrame
    
    Returns:
        DataFrame with comparison metrics
    """
    df = df.copy()
    df['is_franchise'] = df['belongs_to_collection'].notna()
    df['roi'] = df['revenue_musd'] / df['budget_musd']
    
    return df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'roi': 'median',
        'budget_musd': 'mean',
        'popularity': 'mean',
        'vote_average': 'mean'
    }).rename(index={True: 'Franchise', False: 'Standalone'})

def successful_franchises(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies top franchises by key metrics.
    
    Args:
        df: Cleaned movie DataFrame
    
    Returns:
        DataFrame of top 10 franchises
    """
    df = df[df['belongs_to_collection'].notna()].copy()
    
    return df.groupby('belongs_to_collection').agg(
        total_movies=('id', 'count'),
        total_budget_musd=('budget_musd', 'sum'),
        mean_budget_musd=('budget_musd', 'mean'),
        total_revenue_musd=('revenue_musd', 'sum'),
        mean_revenue_musd=('revenue_musd', 'mean'),
        mean_rating=('vote_average', 'mean')
    ).sort_values('total_revenue_musd', ascending=False).head(10)

def successful_directors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies top directors by key metrics.
    
    Args:
        df: Cleaned movie DataFrame
    
    Returns:
        DataFrame of top 10 directors
    """
    return df.groupby('director').agg(
        total_movies=('id', 'count'),
        total_revenue_musd=('revenue_musd', 'sum'),
        mean_rating=('vote_average', 'mean')
    ).sort_values('total_revenue_musd', ascending=False).head(10)

# ===============================
# Session 7: Data Visualization
# ===============================
def generate_visualizations(df: pd.DataFrame) -> None:
    """
    Generates visualizations with proper labeling for analysis.
    
    Args:
        df: Cleaned movie DataFrame
    """
    df = df.copy()
    df['roi'] = df['revenue_musd'] / df['budget_musd']
    df['year'] = df['release_date'].dt.year
    df['is_franchise'] = df['belongs_to_collection'].notna()
    
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = [10, 6]
    
    # Plot 1: Revenue vs Budget
    plt.figure()
    sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', alpha=0.6)
    plt.title("Revenue vs Budget for Movies", fontsize=14, pad=15)
    plt.xlabel("Budget (Million USD)", fontsize=12)
    plt.ylabel("Revenue (Million USD)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('revenue_vs_budget.png')
    plt.close()
    
    # Plot 2: ROI by Genre
    genre_df = df.dropna(subset=['genres']).assign(
        genre_split=df['genres'].str.split('|')
    ).explode('genre_split')
    
    plt.figure()
    sns.boxplot(data=genre_df, x='genre_split', y='roi')
    plt.xticks(rotation=45, ha='right')
    plt.title("ROI Distribution by Genre", fontsize=14, pad=15)
    plt.xlabel("Genre", fontsize=12)
    plt.ylabel("Return on Investment (ROI)", fontsize=12)
    plt.tight_layout()
    plt.savefig('roi_by_genre.png')
    plt.close()
    
    # Plot 3: Popularity vs Rating
    plt.figure()
    sns.scatterplot(data=df, x='popularity', y='vote_average', alpha=0.6)
    plt.title("Popularity vs Average Rating", fontsize=14, pad=15)
    plt.xlabel("Popularity Score", fontsize=12)
    plt.ylabel("Average Rating", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('popularity_vs_rating.png')
    plt.close()
    
    # Plot 4: Yearly Revenue Trends
    yearly = df.groupby('year')['revenue_musd'].mean().dropna()
    plt.figure()
    yearly.plot(marker='o', linestyle='-', linewidth=2)
    plt.title("Average Movie Revenue by Year", fontsize=14, pad=15)
    plt.xlabel("Release Year", fontsize=12)
    plt.ylabel("Average Revenue (Million USD)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('yearly_revenue.png')
    plt.close()
    
    # Plot 5: Franchise vs Standalone
    plt.figure()
    sns.barplot(data=df, x='is_franchise', y='revenue_musd')
    plt.xticks([0, 1], ['Standalone', 'Franchise'])
    plt.title("Revenue Comparison: Franchise vs Standalone", fontsize=14, pad=15)
    plt.xlabel("Movie Type", fontsize=12)
    plt.ylabel("Revenue (Million USD)", fontsize=12)
    plt.savefig('franchise_vs_standalone.png')
    plt.close()