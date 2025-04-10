#1 drop columns
import pandas as pd

def drop_columns(df, columns_to_drop):
    df.drop(columns=columns_to_drop, inplace=True)
    return df

columns_to_drop = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
drop_columns(df, columns_to_drop)

#2,3.evaluate json columns
import ast


def clean_dict_columns(df):
    """
    Cleans specified dictionary/list columns in the DataFrame by extracting the 'name' key
    and replaces original columns with cleaned string values.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame to process.
    
    Returns:
    pd.DataFrame: The DataFrame with cleaned columns.
    """

    def extract_name_from_dict(obj, key='name'):
        try:
            obj = ast.literal_eval(obj) if isinstance(obj, str) else obj
            if isinstance(obj, dict):
                return obj.get(key)
            elif isinstance(obj, list):
                return '|'.join(item.get(key, '') for item in obj if isinstance(item, dict))
        except:
            return None

    columns_to_clean = [
        'belongs_to_collection',
        'genres',
        'spoken_languages',
        'production_countries',
        'production_companies'
    ]

    for col in columns_to_clean:
        df[col] = df[col].apply(lambda x: extract_name_from_dict(x))

    return df


clean_dict_columns(df)

#3 convert column dtypes

import pandas as pd

def convert_columns(df, numeric_cols=None, datetime_col=None):
    """
    Converts specified columns in the DataFrame to appropriate data types.

    Parameters:
    df (pd.DataFrame): The input DataFrame to modify.
    numeric_cols (list, optional): List of column names to convert to numeric.
    datetime_col (str, optional): Name of the column to convert to datetime.

    Returns:
    pd.DataFrame: The DataFrame with converted columns.
    """
    if numeric_cols:
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if datetime_col:
        df[datetime_col] = pd.to_datetime(df[datetime_col], errors='coerce')
    
    return df

numeric_columns = ['budget', 'id', 'popularity']
datetime_column = 'release_date'

df = convert_columns(df, numeric_cols=numeric_columns, datetime_col=datetime_column)


# convert column to M
def convert_to_millions(df, cols):
    """
    Converts specified columns to millions by dividing by 1,000,000.
    
    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    cols (list): List of column names to convert.
    
    Returns:
    pd.DataFrame: The DataFrame with updated columns.
    """
    for col in cols:
        df[col] = df[col] / 1_000_000
    return df

df = convert_to_millions(df, ['budget', 'revenue'])


#. remove dublicates and drop drop rows with unkown id
def clean_duplicates_and_missing(df, subset_cols=['id', 'title']):
    """
    Removes duplicate rows based on given columns and drops rows with missing values in those columns.

    Parameters:
    df (pd.DataFrame): The DataFrame to clean.
    subset_cols (list): List of column names to check for duplicates and missing values.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    df.drop_duplicates(subset=subset_cols, inplace=True)
    df.dropna(subset=subset_cols, inplace=True)
    return df


df = clean_duplicates_and_missing(df)

#filter na rows
def filter_min_non_na(df, min_non_na=10):
    """
    Keeps only rows that have at least `min_non_na` non-NaN values.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.
    min_non_na (int): Minimum number of non-NaN values required.

    Returns:
    pd.DataFrame: Filtered DataFrame.
    """
    return df[df.notna().sum(axis=1) >= min_non_na]

df = filter_min_non_na(df)


#filter Filter to include only 'Released' movies, then drop 'status'.
def filter_released_movies(df):
    """
    Filters DataFrame to include only rows where 'status' is 'Released',
    then drops the 'status' column.

    Parameters:
    df (pd.DataFrame): The DataFrame to filter.

    Returns:
    pd.DataFrame: Filtered DataFrame.
    """
    df = df[df['status'] == 'Released']
    df.drop(columns=['status'], inplace=True)
    return df


df = filter_released_movies(df)


import pandas as pd

def extract_cast_crew(df, credits_col='credits'):
    """
    Extracts cast and crew info from a JSON-like column in the DataFrame.

    - Extracts top 5 cast names (joined with '|')
    - Cast list size
    - Director name
    - Crew list size

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    credits_col (str): Name of the column containing the credits JSON.

    Returns:
    pd.DataFrame: DataFrame with added 'cast', 'cast_size', 'director', and 'crew_size' columns.
    """

#to extract cast json column
    def extract_cast_crew_info(credits_dict):
        if not isinstance(credits_dict, dict):
            return pd.Series([None, None, None, None], index=['cast', 'cast_size', 'director', 'crew_size'])

        cast_list = credits_dict.get('cast', [])
        crew_list = credits_dict.get('crew', [])

        cast_names = [member['name'] for member in cast_list[:5] if 'name' in member]
        directors = [member['name'] for member in crew_list if member.get('job') == 'Director']

        return pd.Series([
            '|'.join(cast_names),
            len(cast_list),
            directors[0] if directors else None,
            len(crew_list)
        ], index=['cast', 'cast_size', 'director', 'crew_size'])

    cast_crew_df = df[credits_col].apply(extract_cast_crew_info)
    df = pd.concat([df, cast_crew_df], axis=1)
    return df

df = extract_cast_crew(df)


#arrange columns
def rearrange_columns(df, rich_order):
    """
    Reorders the columns of the DataFrame to match the rich_order list.

    Parameters:
    df (pd.DataFrame): The DataFrame to reorder.
    rich_order (list): List of column names in the desired order.

    Returns:
    pd.DataFrame: Reordered DataFrame with any remaining columns placed at the end.
    """
    remaining_cols = [col for col in df.columns if col not in rich_order]
    new_order = rich_order + remaining_cols
    return df[new_order]


rich_order = [
    'id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
    'original_language', 'budget_musd', 'revenue_musd', 'production_companies',
    'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime',
    'overview', 'spoken_languages', 'poster_path', 'cast', 'cast_size', 'director', 'crew_size'
]

df = rearrange_columns(df, rich_order)










