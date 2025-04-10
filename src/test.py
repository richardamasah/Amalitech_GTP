#testing my functions
deleted columns = drop_columns(data)

# Convert release_date to datetime and extract year
df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year

yearly_trends = df.groupby('release_year')[['revenue_musd', 'budget_musd']].mean().dropna()

plt.figure(figsize=(12, 6))
yearly_trends.plot(kind='line', marker='o')
plt.title('Yearly Trends: Avg Revenue & Budget')
plt.xlabel('Release Year')
plt.ylabel('Million USD')
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='popularity', y='vote_average', alpha=0.6)
plt.title('Popularity vs Rating')
plt.xlabel('Popularity')
plt.ylabel('Average Rating')
plt.tight_layout()
plt.show()




