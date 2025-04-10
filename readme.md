# 🎬 Movie Data Analysis Project

This project explores a dataset of popular movies using **Python**, **Pandas**, **Matplotlib**, and **Seaborn**. The goal was to understand financial trends, genre performance, and audience behavior in the film industry.

---

## 📂 Project Overview

The analysis walks through key questions:
- Which genres and directors are most successful?
- What are the patterns between budget, revenue, and ROI?
- How do standalone movies compare to franchise films?
- Does popularity match critical acclaim?

---

## 🛠️ Tools & Libraries

- Python
- Pandas
- Matplotlib
- Seaborn
- Jupyter Notebook

---

## 📊 Steps in the Analysis

1. **Data Cleaning**  
   - Removed duplicated columns (`cast`, `director`, etc.)
   - Handled missing values in critical columns like `director`, `genres`, and `revenue_musd`
   - Fixed genres from pipe-delimited strings to lists

2. **Feature Engineering**  
   - Created a new column: `profit = revenue_musd - budget_musd`
   - Calculated `ROI = profit / budget_musd`
   - Extracted main genre from the list of genres
   - Flagged movies belonging to a franchise (`belongs_to_collection`)

3. **Shortlisting Columns**  
   Reduced columns to the most relevant for our analysis (like `budget_musd`, `revenue_musd`, `vote_average`, `genres`, `popularity`, etc.)

4. **Visualizations**  
   Created plots to highlight trends using Matplotlib and Seaborn:
   - Revenue vs. Budget
   - ROI Distribution by Genre
   - Popularity vs. Rating
   - Yearly Revenue Trends
   - Franchise vs. Standalone Comparison
   - Top Directors by Revenue

5. **Anomaly Detection**  
   - Used `.value_counts()` to spot strange formatting and inconsistent genre or country entries
   - Noted inconsistencies like multiple `director` columns or pipe-separated genres

---

## 📈 Insights & Visualizations

### 🎯 Revenue vs. Budget  
A scatter plot showed a **positive correlation** between budget and revenue, but with several **outliers**. Some low-to-mid budget films performed exceptionally well, suggesting that **strong scripts or franchises** can drive profits without huge investments.

### 📦 ROI by Genre  
Using a boxplot, we compared genres by ROI. Genres like **Animation**, **Family**, and **Horror** had **higher returns on investment**, while **Drama** and **Romance** were more inconsistent and lower-yielding, possibly due to niche appeal.

### 🌟 Popularity vs. Rating  
A scatter plot showed **little correlation** between popularity and critical rating. Many highly popular movies had average ratings — suggesting that **hype ≠ quality**. Conversely, some highly-rated movies weren’t widely popular.

### 📆 Yearly Revenue Trends  
Revenue has generally **increased over the years**, especially after 2000. Notable spikes correspond to big franchise releases. A dip around 2020 likely reflects the impact of **COVID-19** on cinema.

### 🔁 Franchise vs. Standalone  
Movies that are part of a **collection/franchise** consistently showed **higher revenue and ROI** than standalone films. This supports the idea that sequels and familiar characters draw more viewers.

### 🎬 Top Directors  
Directors like **James Cameron**, **Christopher Nolan**, and **Anthony & Joe Russo** ranked highest in total revenue. This suggests that industry success often clusters around **a few high-performing directors**.

---

## 🔎 Observed Anomalies

- The `genres` column originally had long pipe-delimited strings like `Action|Adventure|Sci-Fi` instead of lists.
- `production_countries` sometimes mixed countries in different orders (`USA|UK` vs `UK|USA`).
- Duplicated column names were present (e.g., `cast`, `director`, `crew_size` appeared more than once).
- Some directors had `None` or blank entries that had to be filtered out for grouping.

---

## ✅ Things Done Well

- 🧼 Cleaned messy columns and fixed structural issues in the dataset
- 💡 Created new features like ROI and profit that drove real insight
- 📉 Used a mix of scatter plots, boxplots, and line charts to show different relationships
- 🔎 Spotted anomalies using `value_counts()` and fixed them before analysis
- 🧠 Explained each chart in terms of **business insight**, not just visual trend

---

## 📁 Files Included

- `notebook1.ipynb`: Full analysis and visualizations
- `README.md`: Summary of steps, tools, insights, and results

---

