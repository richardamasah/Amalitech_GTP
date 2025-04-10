

#revenue vs budgetplt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', hue='original_language', alpha=0.7)
plt.title('Revenue vs Budget')
plt.xlabel('Budget (Million USD)')
plt.ylabel('Revenue (Million USD)')
plt.legend(title='Language', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
