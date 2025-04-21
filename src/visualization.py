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

generate_visualizations(df_cleaned)
