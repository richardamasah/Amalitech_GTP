import pandas as pd
import requests
import os
from dotenv import load_dotenv
from typing import List

# ===============================
#  Load API Key from .env File
# ===============================
load_dotenv()  # Looks for .env in same directory
api_key = os.getenv("API_KEY")


# ==================================================
#  Function: Fetch movie data by TMDB movie IDs
# ==================================================
def fetch_movie_data(movie_ids: List[int], api_key: str) -> pd.DataFrame:
    """
    Fetches movie details from TMDB API for a list of movie IDs.
    
    Parameters:
        movie_ids (List[int]): A list of TMDB movie IDs.
        api_key (str): My TMDB API key.
        
    Returns:
        pd.DataFrame: A DataFrame of movie data.
    """
    base_url = "https://api.themoviedb.org/3/movie/{}"
    params = {
        "api_key": api_key,
        "append_to_response": "credits"
    }

    movie_ids = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513
]

    all_data = []

    for movie_id in movie_ids:
        try:
            response = requests.get(base_url.format(movie_id), params=params)
            
            # Handle invalid or missing movies
            if response.status_code == 200:
                all_data.append(response.json())
            else:
                print(f" Movie ID {movie_id} not found. Status: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f" Network error while fetching Movie ID {movie_id}: {e}")

     #  Save fetched data to cache
    #with open(cache_file, 'w', encoding='utf-8') as f:
     #   json.dump(all_data, f, indent=2)
    
    # Return as DataFrame
    return pd.DataFrame(all_data)






# ================================================
#                 STEP 2
#           DATA CLEANING AND PREPROCESSING
#============================================


import pandas as pd
import numpy as np



def clean_basic_movie_data(df):
    """
    Cleans TMDB movie data by:
    - Dropping irrelevant columns
    - Flattening JSON-like fields (genres, countries, languages, etc.)
    - Handling missing/unrealistic values
    - Converting data types
    - Filtering only 'Released' movies
    - Reordering columns for final dataset

    Parameters:
        df (pd.DataFrame): Raw TMDB movie DataFrame

    Returns:
        pd.DataFrame: Cleaned and structured DataFrame
    """

    # --------------------------------------
    # 1. Drop irrelevant columns
    # --------------------------------------
    to_drop = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    df.drop(columns=to_drop, inplace=True, errors='ignore')

    # --------------------------------------
    # 2. Clean JSON-like columns (overwrite)
    # --------------------------------------
    df['belongs_to_collection'] = df['belongs_to_collection'].apply(
        lambda x: x['name'] if isinstance(x, dict) else np.nan
    )

    df['genres'] = df['genres'].apply(
        lambda x: "|".join([g['name'] for g in x]) if isinstance(x, list) else np.nan
    )

    df['production_countries'] = df['production_countries'].apply(
        lambda x: "|".join([c['name'] for c in x]) if isinstance(x, list) else np.nan
    )

    df['spoken_languages'] = df['spoken_languages'].apply(
        lambda x: "|".join([l['english_name'] for l in x]) if isinstance(x, list) else np.nan
    )

    df['production_companies'] = df['production_companies'].apply(
        lambda x: "|".join([p['name'] for p in x]) if isinstance(x, list) else np.nan
    )

    # --------------------------------------
    # 3. Convert data types (handle errors)
    # --------------------------------------
    df['id'] = pd.to_numeric(df['id'], errors='coerce')
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # --------------------------------------
    # 4. Replace unrealistic values
    # --------------------------------------
    df[['budget', 'revenue', 'runtime']] = df[['budget', 'revenue', 'runtime']].replace(0, np.nan)

    # Convert budget and revenue to millions
    df['budget'] = df['budget'] / 1_000_000
    df['revenue'] = df['revenue'] / 1_000_000

    # Fix vote_count = 0 with high vote_average (likely invalid)
    df.loc[(df['vote_count'] == 0) & (df['vote_average'] > 0), 'vote_average'] = np.nan

    # Clean placeholders in text
    for col in ['overview', 'tagline']:
        df[col] = df[col].replace(['No Data', 'null', '', 'None'], np.nan)

    # --------------------------------------
    # 5. Remove bad rows
    # --------------------------------------
    df = df.drop_duplicates(subset='id')
    df = df.dropna(subset=['id', 'title'])
    df = df[df.notna().sum(axis=1) >= 10]
    df = df[df['status'] == 'Released']
    df.drop(columns='status', inplace=True, errors='ignore')

    

    return df








import json

def extract_credits_fields(df):
    """
    Extracts structured fields from the 'credits' JSON-like column:
    - First 3 cast names
    - Cast size
    - Crew size
    - Director name

    Parameters:
        df (pd.DataFrame): DataFrame containing a 'credits' column as stringified JSON

    Returns:
        pd.DataFrame: Updated DataFrame with new fields and 'credits' removed
    """

    # Helper function to safely parse credits
    def parse_credits(x):
        try:
            return json.loads(x) if isinstance(x, str) else x
        except Exception:
            return {}

    # Parse 'credits' JSON string into dict
    df['credits_parsed'] = df['credits'].apply(parse_credits)

    # Extract cast names
    def get_main_cast(credit_obj):
        try:
            cast = credit_obj.get('cast', [])
            return ", ".join([actor['name'] for actor in cast[:3]])  # top 3
        except:
            return np.nan

    # Get cast and crew size
    def get_cast_size(credit_obj):
        return len(credit_obj.get('cast', [])) if isinstance(credit_obj, dict) else np.nan

    def get_crew_size(credit_obj):
        return len(credit_obj.get('crew', [])) if isinstance(credit_obj, dict) else np.nan

    # Extract director name
    def get_director(credit_obj):
        if isinstance(credit_obj, dict):
            for person in credit_obj.get('crew', []):
                if person.get('job') == 'Director':
                    return person.get('name')
        return np.nan

    # Create new columns
    df['main_cast'] = df['credits_parsed'].apply(get_main_cast)
    df['cast_size'] = df['credits_parsed'].apply(get_cast_size)
    df['crew_size'] = df['credits_parsed'].apply(get_crew_size)
    df['director'] = df['credits_parsed'].apply(get_director)

    # Drop original credits and parsed credits columns
    df.drop(columns=['credits', 'credits_parsed'], inplace=True, errors='ignore')

    return df




# kpi_analysis.py

import pandas as pd

# ===============================================
# KPI Analysis Functions for TMDb Movie Dataset
# ===============================================

def rank_movies(df):
    """
    Ranks movies based on various performance metrics.
    Includes filters for ROI (budget ≥ 10M) and rating (votes ≥ 10).
    Returns a dictionary of top-ranked DataFrames.
    """
    df = df.copy()
    df['profit'] = df['revenue'] - df['budget']
    df['roi'] = df['revenue'] / df['budget']

    roi_df = df[df['budget'] >= 10]
    rated_df = df[df['vote_count'] >= 10]

    def top_n(data, column, ascending=False, n=10):
        return data.sort_values(by=column, ascending=ascending).head(n)

    results = {
        'highest_revenue': top_n(df, 'revenue'),
        'highest_budget': top_n(df, 'budget'),
        'highest_profit': top_n(df, 'profit'),
        'lowest_profit': top_n(df, 'profit', ascending=True),
        'highest_roi': top_n(roi_df, 'roi'),
        'lowest_roi': top_n(roi_df, 'roi', ascending=True),
        'most_voted': top_n(df, 'vote_count'),
        'highest_rated': top_n(rated_df, 'vote_average'),
        'lowest_rated': top_n(rated_df, 'vote_average', ascending=True),
        'most_popular': top_n(df, 'popularity')
    }

    return results


def compare_franchises(df):
    """
    Compares franchise vs. standalone movies across key metrics:
    Mean revenue, median ROI, mean budget, popularity, and rating.
    """
    df = df.copy()
    df['is_franchise'] = df['belongs_to_collection'].notnull()
    df['roi'] = df['revenue'] / df['budget']

    grouped = df.groupby('is_franchise').agg({
        'revenue': 'mean',
        'roi': 'median',
        'budget': 'mean',
        'popularity': 'mean',
        'vote_average': 'mean'
    }).rename(index={True: 'Franchise', False: 'Standalone'})

    return grouped


def successful_franchises(df):
    """
    Returns top 10 most successful franchises based on:
    Total movies, budget, revenue, and mean rating.
    """
    df = df[df['belongs_to_collection'].notnull()].copy()
    df['collection_name'] = df['belongs_to_collection'].apply(
        lambda x: x.get('name') if isinstance(x, dict) else None
    )

    grouped = df.groupby('collection_name').agg(
        total_movies=('id', 'count'),
        total_budget=('budget', 'sum'),
        mean_budget=('budget', 'mean'),
        total_revenue=('revenue', 'sum'),
        mean_revenue=('revenue', 'mean'),
        mean_rating=('vote_average', 'mean')
    ).sort_values(by='total_revenue', ascending=False)

    return grouped.head(10)


def successful_directors(df):
    """
    Returns top 10 most successful directors based on:
    Movie count, total revenue, and average rating.
    """
    grouped = df.groupby('director').agg(
        total_movies=('id', 'count'),
        total_revenue=('revenue', 'sum'),
        mean_rating=('vote_average', 'mean')
    ).sort_values(by='total_revenue', ascending=False)

    return grouped.head(10)





import matplotlib.pyplot as plt
import seaborn as sns

def generate_visualizations(df):
    """
    Generates individual plots for:
    - Revenue vs Budget
    - ROI by Genre
    - Popularity vs Rating
    - Yearly Revenue Trends
    - Franchise vs Standalone Comparison
    """

    # Prepare working copy
    df = df.copy()
    df['roi'] = df['revenue'] / df['budget']
    df['year'] = df['release_date'].dt.year
    df['is_franchise'] = df['belongs_to_collection'].notna()

    sns.set(style="whitegrid")

    # 1. Revenue vs Budget
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x='budget', y='revenue')
    plt.title("Revenue vs Budget")
    plt.xlabel("Budget (Million USD)")
    plt.ylabel("Revenue (Million USD)")
    plt.show()

    # 2. ROI Distribution by Genre
    genre_df = df.dropna(subset=['genres']).copy()
    genre_df = genre_df.assign(genre_split=genre_df['genres'].str.split('|')).explode('genre_split')

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=genre_df, x='genre_split', y='roi')
    plt.xticks(rotation=90)
    plt.title("ROI by Genre")
    plt.xlabel("Genre")
    plt.ylabel("ROI")
    plt.show()

    # 3. Popularity vs Rating
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df, x='popularity', y='vote_average')
    plt.title("Popularity vs Rating")
    plt.xlabel("Popularity")
    plt.ylabel("Average Rating")
    plt.show()

    # 4. Yearly Revenue Trend
    yearly = df.groupby('year')['revenue'].mean().dropna()
    plt.figure(figsize=(10, 5))
    yearly.plot(marker='o')
    plt.title("Average Revenue by Year")
    plt.xlabel("Year")
    plt.ylabel("Avg Revenue (Million USD)")
    plt.grid(True)
    plt.show()

    # 5. Franchise vs Standalone Revenue Comparison
    plt.figure(figsize=(6, 4))
    sns.barplot(data=df, x='is_franchise', y='revenue')
    plt.xticks([0, 1], ['Standalone', 'Franchise'])
    plt.title("Revenue: Franchise vs Standalone")
    plt.ylabel("Revenue (Million USD)")
    plt.xlabel("Movie Type")
    plt.show()

#from movie_analysis import generate_visualizations

#generate_visualizations(df_cleaned)






