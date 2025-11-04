# src/score_sites.py
import pandas as pd
import numpy as np
from datetime import datetime


def compute_recency_score(df: pd.DataFrame, date_col: str = 'LastUpdatePostDate') -> pd.Series:
    """Return a 0-1 recency score where 1 is most recent."""
    now = pd.Timestamp.now()
    if date_col not in df.columns:
        return pd.Series(0.0, index=df.index)

    dates = pd.to_datetime(df[date_col], errors='coerce')
    days = (now - dates).dt.days.clip(lower=0)
    score = np.exp(-days / 365.0)  # recent = high score
    return score.fillna(0.0)


def compute_enrollment_score(df: pd.DataFrame, col: str = 'EnrollmentCount') -> pd.Series:
    """Normalize enrollment counts between 0 and 1 using log scale."""
    if col not in df.columns:
        return pd.Series(0.0, index=df.index)
    vals = df[col].astype(float).fillna(0.0)
    vals_log = np.log1p(vals)
    if vals_log.max() == vals_log.min():
        return pd.Series(0.0, index=df.index)
    return (vals_log - vals_log.min()) / (vals_log.max() - vals_log.min())


def compute_scores(df: pd.DataFrame,
                   weights: dict = None,
                   date_col: str = 'LastUpdatePostDate') -> pd.DataFrame:
    """Return df with added score columns and a final 'score'."""

    df = df.copy()
    if weights is None:
        weights = {'completeness': 0.4, 'enrollment': 0.3, 'recency': 0.3}

    if 'completeness' not in df.columns:
        df['completeness'] = 0.0

    recency = compute_recency_score(df, date_col=date_col)
    enrollment = compute_enrollment_score(df, col='EnrollmentCount')
    completeness = df['completeness'].astype(float).fillna(0.0)

    df['recency_score'] = recency
    df['enrollment_score'] = enrollment
    df['completeness_score'] = completeness

    # Weighted final score
    df['score'] = (
        weights.get('completeness', 0) * df['completeness_score'] +
        weights.get('enrollment', 0) * df['enrollment_score'] +
        weights.get('recency', 0) * df['recency_score']
    )

    # Scale to 0–100
    min_s, max_s = df['score'].min(), df['score'].max()
    if pd.notnull(min_s) and max_s > min_s:
        df['score_pct'] = 100 * (df['score'] - min_s) / (max_s - min_s)
    else:
        df['score_pct'] = df['score'] * 100

    return df
