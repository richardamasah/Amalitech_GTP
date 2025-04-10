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









