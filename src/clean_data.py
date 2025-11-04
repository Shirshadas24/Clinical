# src/clean_data.py
import pandas as pd

def extract_nested_value(d, keys):
    """Safely extracts nested value from dict using a list of keys."""
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return None
    return d


def clean_trials(df: pd.DataFrame) -> pd.DataFrame:
    print("▶️ Initial shape:", df.shape)
    print("▶️ Initial columns sample:", list(df.columns)[:5])

    df = df.copy()

    # df = df.dropna(axis=1, how='all')
    cols_to_drop = [col for col in df.columns if df[col].isna().all() and col != 'Location']
    df = df.drop(columns=cols_to_drop)

    if 'Location' not in df.columns:
        df['Location'] = 'Unknown'
    else:
        df['Location'] = df['Location'].fillna('Unknown')

    print(" After dropping all-NaN columns:", df.shape)

    for col in df.columns:
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)

    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace(".", "_")
    )
    print(" After renaming columns:", list(df.columns)[:5])

    df = df.drop_duplicates().reset_index(drop=True)
    print(" Final shape:", df.shape)

    return df