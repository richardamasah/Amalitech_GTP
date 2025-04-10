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






