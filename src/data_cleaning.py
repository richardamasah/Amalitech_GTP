import pandas as pd

def drop_columns(df, columns_to_drop):
    df.drop(columns=columns_to_drop, inplace=True)
    return df

columns_to_drop = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
drop_columns(df, columns_to_drop)




