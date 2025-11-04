# file: src/database.py
"""Simple SQLite persistence helpers."""
import sqlite3
import pandas as pd
from typing import Union


def save_to_sqlite(df: pd.DataFrame, path: str, table: str = 'records', if_exists: str = 'replace') -> None:
    """Save DataFrame to sqlite. Default replaces the table each time.

    - df: DataFrame to save
    - path: path to sqlite file
    - table: table name
    - if_exists: 'replace' | 'append'
    """
    conn = sqlite3.connect(path)
    try:
        df.to_sql(table, conn, if_exists=if_exists, index=False)
    finally:
        conn.close()


def load_from_sqlite(path: str, table: str = 'records') -> pd.DataFrame:
    conn = sqlite3.connect(path)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    finally:
        conn.close()
    return df



