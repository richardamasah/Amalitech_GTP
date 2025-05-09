# TMDB Movie Analysis Pipeline
# This script calls functions from tmdb_movie_analysis.py individually to execute the movie data analysis pipeline.
# Copy and paste each section into a Jupyter Notebook cell for execution.

# Import required functions from tmdb_movie_analysis.py
from tmdb_movie_analysis import (
    fetch_movie_data,
    clean_basic_movie_data,
    extract_credits_fields,
    calculate_kpis,
    filter_movies,
    compare_franchises,
    successful_franchises,
    successful_directors,
    generate_visualizations,
    MOVIE_IDS,
    API_KEY
)
import pandas as pd

# Set pandas display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ===============================
# Session 1: Fetch Movie Data
# ===============================
# Fetch raw movie data from TMDB API
raw_df = fetch_movie_data(MOVIE_IDS, API_KEY)
print("Raw DataFrame shape:", raw_df.shape)
raw_df.head()

# ===============================
# Session 2: Clean Movie Data
# ===============================
# Clean and preprocess the raw movie data
cleaned_df = clean_basic_movie_data(raw_df)
print("Cleaned DataFrame shape:", cleaned_df.shape)
cleaned_df.head()

# ===============================
# Session 3: Extract Credits Information
# ===============================
# Extract cast, crew, and director information
credits_df = extract_credits_fields(cleaned_df)
print("DataFrame with credits shape:", credits_df.shape)
credits_df[['id', 'title', 'main_cast', 'cast_size', 'crew_size', 'director']].head()

# ===============================
# Session 4: Calculate KPIs
# ===============================
# Calculate key performance indicators and rank movies
kpi_results = calculate_kpis(credits_df)
# Display each KPI result
for kpi_name, kpi_df in kpi_results.items():
    print(f"\n{kpi_name.replace('_', ' ').title()}:")
    print(kpi_df)

# ===============================
# Session 5: Advanced Filtering
# ===============================
# Perform advanced filtering for specific queries
filter_results = filter_movies(credits_df)
# Display filter results
print("\nScience Fiction Action Movies with Bruce Willis:")
print(filter_results['sci_fi_action_willis'])
print("\nUma Thurman Movies Directed by Quentin Tarantino:")
print(filter_results['thurman_tarantino'])

# ===============================
# Session 6: Franchise and Director Analysis
# ===============================
# Compare franchises vs standalone movies
franchise_comparison = compare_franchises(credits_df)
print("\nFranchise vs Standalone Comparison:")
print(franchise_comparison)

# Identify top franchises
top_franchises = successful_franchises(credits_df)
print("\nTop Franchises:")
print(top_franchises)

# Identify top directors
top_directors = successful_directors(credits_df)
print("\nTop Directors:")
print(top_directors)

# ===============================
# Session 7: Generate Visualizations
# ===============================
# Generate and save visualizations as PNG files
generate_visualizations(credits_df)
print("Visualizations saved as PNG files: revenue_vs_budget.png, roi_by_genre.png, popularity_vs_rating.png, yearly_revenue.png, franchise_vs_standalone.png")