### ✅ Project Steps: TMDB Movie Data Analysis

#### 1. **Data Loading & Merging**
- Loaded a base dataset (`mdata.csv`) with movie metadata.
- Retrieved additional movie information (e.g., cast, crew, budget, revenue) using the TMDB API.
- Merged API results into the main dataframe.

#### 2. **Data Cleaning**
- Converted `budget` and `revenue` columns into millions (MUSD).
- Removed duplicated columns (e.g., multiple `cast`, `director`, `crew_size` columns).
- Checked for and dropped rows with missing or invalid values in important fields like `director`, `genres`, and `revenue_musd`.
- Extracted clean fields such as `main_genre` from unordered genre strings.

#### 3. **Feature Engineering**
- Created new columns:
  - `profit` = revenue - budget
  - `roi` = revenue / budget
  - `cast_size` and `crew_size` from parsed JSON
- Converted `release_date` into datetime format and extracted `release_year` for trend analysis.

#### 4. **Anomaly Detection**
- Identified irregularities in:
  - `genres` (unordered combinations and inconsistent formats)
  - `production_countries` (e.g., 'United States|UK' vs 'UK|United States')
- Used `.value_counts()` to examine categories and frequencies for anomalies.

#### 5. **Exploratory Data Analysis & Filtering**
- Filtered to keep movies with valid numeric data (e.g., non-zero budgets and revenue).
- Removed rows with missing or non-string genres.
- Ensured director column was one-dimensional and string-based.

#### 6. **Visualizations and Insights**
- **Revenue vs Budget**: Clear positive correlation; high-budget films tend to earn more, but ROI doesn't always increase.
- **ROI by Genre**: Family, Animation, and Comedy genres often achieve higher ROI despite moderate revenue—suggesting budget efficiency.
- **Popularity vs Rating**: Scatterplot showed that popularity doesn’t always align with rating—some low-rated movies still trend.
- **Yearly Trends**: Revenue increases over time; blockbusters more common in recent years.
- **Franchise vs Standalone**: Movies part of a collection tend to generate more revenue and often higher ROI, highlighting the power of brand/franchise loyalty.

#### 7. **Top Directors**
- Grouped by `director` to find top performers by:
  - Number of movies
  - Total revenue
  - Average rating
- Allowed identification of consistently successful directors like James Cameron, Anthony Russo, etc.

