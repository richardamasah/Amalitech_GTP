# 🎬 TMDB Movie Data Analysis

This project explores a movie dataset enriched with The Movie Database (TMDB) API. It aims to uncover insights about movie success factors using Python libraries like Pandas, Matplotlib, and Seaborn.

---

## 📂 Data Sources

- TMDB API (`credits`, `budget`, `revenue`, etc.)
- Local CSV file with movie metadata

---

## 🔧 Data Cleaning Steps

- Converted `budget` and `revenue` into millions (MUSD)
- Removed redundant or duplicate columns
- Extracted features from nested JSONs (`credits`, `genres`)
- Dealt with anomalies in columns like `genres`, `production_countries`, and missing values

---

## 📊 Key KPIs

- **Total Revenue**
- **Return on Investment (ROI)**
- **Popularity**
- **Mean Rating**

---

## 📈 Visualizations

- **Revenue vs Budget**: Scatterplot showing correlation
- **ROI by Genre**: Boxplot to visualize distribution
- **Popularity vs. Rating**: Detects outliers and general patterns
- **Annual Revenue Trends**: Shows evolution of box office success
- **Franchise vs. Standalone**: Highlights the impact of being part of a series

---

## 💡 Insights

- Action and Science Fiction genres dominate high-revenue segments.
- ROI is not always highest in big-budget films—animated and family genres have surprising efficiency.
- Franchise movies (those belonging to collections) generally outperform standalone films in both revenue and ROI.
- The dataset contains genre duplication anomalies due to unordered combinations.

---

## 📦 Libraries Used

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `requests`
