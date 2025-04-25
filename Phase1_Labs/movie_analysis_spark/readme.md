Movie Data Analysis with PySpark
Overview
This project analyzes movie data from the TMDB API using PySpark. It fetches movie data, cleans and processes it, performs analyses like ranking movies by revenue and comparing franchises, and creates visualizations such as revenue vs. budget plots. The project includes a Python script for automation and a Jupyter Notebook for interactive analysis.
Objectives

Fetch and clean movie data.
Analyze metrics like revenue and popularity.
Compare franchise vs. standalone movies.
Create visualizations to explore trends.

Prerequisites

Python 3.11.x
Java JDK 8 (for Spark)
TMDB API Key: Sign up at themoviedb.org
Git

Getting Started
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

Usage
Running the Script

Activate the virtual environment.
Run the main script:python main_script.py


Output: Fetches data, performs analysis, and saves visualizations.

Running the Jupyter Notebook

Activate the virtual environment.
Launch Jupyter:jupyter notebook


Open the notebook, select the venv kernel, and run cells.

Visualizations
The project generates plots like revenue vs. budget, ROI by genre, and more, saved as PNG files.
Troubleshooting

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
