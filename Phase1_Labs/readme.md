## Movie Data Analysis with PySpark


# Overview
The analysis walks through key questions:

Which genres and directors are most successful?
What are the patterns between budget, revenue, and ROI?
How do standalone movies compare to franchise films?
Does popularity match critical acclaim?

Fetch and clean movie data.
Analyze metrics like revenue and popularity.
Compare franchise vs. standalone movies.
Create visualizations to explore trends.


 ## Tools & Libraries
Python
Pandas
Matplotlib
Seaborn
Jupyter Notebook

## Prerequisites

Python 3.11.x
Java JDK 8 (for Spark)
TMDB API Key: Sign up at themoviedb.org
Git

## Getting Started
1. Clone the Repository
git clone https://github.com/your-username/movie-data-analysis.git
cd movie-data-analysis

2. Set Up Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

3. Install Dependencies
pip install -r requirements.txt

Or manually:
pip install pyspark==3.5.0 pandas matplotlib requests python-dotenv jupyter

4. Set Up for Windows (if applicable)

Download winutils.exe: GitHub Link
Place in C:\hadoop\bin.
Set HADOOP_HOME=C:\hadoop and add C:\hadoop\bin to Path.

5. Configure TMDB API Key
Create a .env file:
API_KEY=your_tmdb_api_key




Activate the virtual environment.
Launch Jupyter:jupyter notebook




📈 Insights & Visualizations

🎯 Revenue vs. Budget
A scatter plot showed a positive correlation between budget and revenue, but with several outliers. Some low-to-mid budget films performed exceptionally well, suggesting that strong scripts or franchises can drive profits without huge investments.

📦 ROI by Genre
Using a boxplot, we compared genres by ROI. Genres like Animation, Family, and Horror had higher returns on investment, while Drama and Romance were more inconsistent and lower-yielding, possibly due to niche appeal.

🌟 Popularity vs. Rating
A scatter plot showed little correlation between popularity and critical rating. Many highly popular movies had average ratings — suggesting that hype ≠ quality. Conversely, some highly-rated movies weren’t widely popular.

📆 Yearly Revenue Trends
Revenue has generally increased over the years, especially after 2000. Notable spikes correspond to big franchise releases. A dip around 2020 likely reflects the impact of COVID-19 on cinema.

🔁 Franchise vs. Standalone
Movies that are part of a collection/franchise consistently showed higher revenue and ROI than standalone films. This supports the idea that sequels and familiar characters draw more viewers.

🎬 Top Directors
Directors like James Cameron, Christopher Nolan, and Anthony & Joe Russo ranked highest in total revenue. This suggests that industry success often clusters around a few high-performing directors.

“Did not find winutils.exe”: Set HADOOP_HOME and Path.
“UnicodeEncodeError”: Add sys.stdout.reconfigure(encoding='utf-8') to the script.
“No module named 'pyspark'”: Activate the virtual environment and install pyspark.

Contributing

Fork the repository.
Create a branch: git checkout -b feature-name.
Commit: git commit -m "Add feature".
Push: git push origin feature-name.
Open a pull request.

License
MIT License. See the LICENSE file.
