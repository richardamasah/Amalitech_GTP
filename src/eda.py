def generate_movie_rankings(df, top_n=10):
    """
    Generates top/bottom movie rankings based on various metrics.

    Metrics covered:
    - Highest Revenue
    - Highest Budget
    - Highest Profit
    - Lowest Profit
    - Highest ROI (Revenue / Budget) where Budget ≥ 10M
    - Lowest ROI (Budget ≥ 10M)
    - Most Voted Movies
    - Highest Rated (vote_count ≥ 10)
    - Lowest Rated (vote_count ≥ 10)
    - Most Popular Movies

    Parameters:
    df (pd.DataFrame): The input movie DataFrame.
    top_n (int): Number of top records to return for each ranking.

    Returns:
    dict: Dictionary with metric names as keys and top ranked DataFrames as values.
    """
    # Prepare necessary columns
    df = df.copy()
    df['profit'] = df['revenue_musd'] - df['budget_musd']
    df['roi'] = df['revenue_musd'] / df['budget_musd']
    
    # Define ranking function
    def rank(df, sort_by, ascending=False, filters=None):
        df_filtered = df.copy()
        if filters is not None:
            df_filtered = df_filtered.query(filters) if isinstance(filters, str) else df_filtered[filters]
        return df_filtered.sort_values(by=sort_by, ascending=ascending).head(top_n)

    # Rankings
    rankings = {
        'Highest Revenue': rank(df, 'revenue_musd'),
        'Highest Budget': rank(df, 'budget_musd'),
        'Highest Profit': rank(df, 'profit'),
        'Lowest Profit': rank(df, 'profit', ascending=True),
        'Highest ROI': rank(df, 'roi', filters='budget_musd >= 10'),
        'Lowest ROI': rank(df, 'roi', filters='budget_musd >= 10', ascending=True),
        'Most Voted': rank(df, 'vote_count'),
        'Highest Rated': rank(df, 'vote_average', filters='vote_count >= 10'),
        'Lowest Rated': rank(df, 'vote_average', filters='vote_count >= 10', ascending=True),
        'Most Popular': rank(df, 'popularity')
    }

    return rankings

movie_rankings = generate_movie_rankings(df)

# print(movie_rankings['Highest Revenue'])


#Filter the dataset for specific queries
def filter_movies(df):
    """
    Filters the movie dataset for specific queries.

    Returns:
    dict: Two DataFrames for each search.
    """

    # --- Search 1 ---
    sci_fi_action_bruce = df[
        df['genres'].str.contains('Science Fiction') &
        df['genres'].str.contains('Action') &
        df['cast'].str.contains('Bruce Willis', case=False, na=False)
    ].sort_values(by='vote_average', ascending=False)

    # --- Search 2 ---
    uma_tarantino = df[
        df['cast'].str.contains('Uma Thurman', case=False, na=False) &
        df['director'].str.contains('Quentin Tarantino', case=False, na=False)
    ].sort_values(by='runtime', ascending=True)

    return {
        'Best Sci-Fi Action with Bruce Willis': sci_fi_action_bruce,
        'Uma Thurman & Tarantino': uma_tarantino
    }

filtered_results = filter_movies(df)

# Example: view top results for each search
print(filtered_results['Best Sci-Fi Action with Bruce Willis'].head())
print(filtered_results['Uma Thurman & Tarantino'].head())


#compare franchise vs standlone
def compare_franchise_vs_standalone(df):
    """
    Compares movie franchises vs. standalone movies on various metrics:
    - Mean Revenue
    - Median ROI
    - Mean Budget
    - Mean Popularity
    - Mean Rating

    Returns:
    pd.DataFrame: Summary table comparing franchises and standalones.
    """

    # Ensure required columns exist
    df = df.copy()
    df['is_franchise'] = df['belongs_to_collection'].notna()
    df['roi'] = df['revenue_musd'] / df['budget_musd']

    # Group by franchise status
    grouped = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'roi': 'median',
        'budget_musd': 'mean',
        'popularity': 'mean',
        'vote_average': 'mean'
    })

    # Rename rows for readability
    grouped.index = ['Standalone', 'Franchise']
    grouped.columns = ['Mean Revenue (M USD)', 'Median ROI', 'Mean Budget (M USD)',
                       'Mean Popularity', 'Mean Rating']

    return grouped

comparison_df = compare_franchise_vs_standalone(df)

#compare franchise n directors
def get_top_franchises(df, top_n=10):
    df = df.copy()
    df['belongs_to_collection'].replace('None', pd.NA, inplace=True)
    franchise_df = df[df['belongs_to_collection'].notna()]

    top_franchises = franchise_df.groupby('belongs_to_collection').agg(
        number_of_movies=('id', 'count'),
        total_budget=('budget_musd', 'sum'),
        mean_budget=('budget_musd', 'mean'),
        total_revenue=('revenue_musd', 'sum'),
        mean_revenue=('revenue_musd', 'mean'),
        mean_rating=('vote_average', 'mean')
    ).sort_values(by='total_revenue', ascending=False)

    return top_franchises.head(top_n)

top_franchises = get_top_franchises(df)
top_franchises






