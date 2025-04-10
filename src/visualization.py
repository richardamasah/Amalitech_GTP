

#revenue vs budgetplt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', hue='original_language', alpha=0.7)
plt.title('Revenue vs Budget')
plt.xlabel('Budget (Million USD)')
plt.ylabel('Revenue (Million USD)')
plt.legend(title='Language', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Franchise vs. Standalone Success
df['is_franchise'] = df['belongs_to_collection'].notna()

comparison = df.groupby('is_franchise').agg({
    'revenue_musd': 'mean',
    'roi': 'median',
    'budget_musd': 'mean',
    'popularity': 'mean',
    'vote_average': 'mean'
}).rename(index={True: 'Franchise', False: 'Standalone'})

comparison.plot(kind='bar', figsize=(12, 6))
plt.title('Franchise vs Standalone: Success Metrics')
plt.ylabel('Average Value')
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.tight_layout()
plt.show()

