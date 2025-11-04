# src/metrics.py
import pandas as pd
import numpy as np
from datetime import datetime

def compute_match_score(df: pd.DataFrame) -> pd.DataFrame:
    """Compute synthetic match score (e.g., condition-region fit)."""
    if df.empty:
        return df

    np.random.seed(42)  # reproducibility
    df["TherapeuticMatch"] = np.random.rand(len(df))
    df["PhaseMatch"] = np.random.rand(len(df))
    df["InterventionMatch"] = np.random.rand(len(df))
    df["RegionMatch"] = np.random.rand(len(df))

    df["MatchScore"] = (
        0.4 * df["TherapeuticMatch"]
        + 0.2 * df["PhaseMatch"]
        + 0.2 * df["InterventionMatch"]
        + 0.2 * df["RegionMatch"]
    )
    return df


def compute_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Compute data completeness and recency quality score."""
    if df.empty:
        return df

    def quality(row):
        filled = row.notna().sum()
        total = len(row)
        recency_weight = 1.0
        if pd.notna(row.get("LastUpdatePostDate")):
            try:
                days_old = (datetime.now() - pd.to_datetime(row["LastUpdatePostDate"])).days
                recency_weight = 1 if days_old < 365 else 0.8
            except Exception:
                pass
        return (filled / total) * recency_weight

    df["DataQuality"] = df.apply(quality, axis=1)
    return df


def compute_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add completion ratio and performance indicators if status info exists."""
    if "OverallStatus" not in df.columns:
        df["CompletedRatio"] = np.nan
        return df

    status_counts = df["OverallStatus"].value_counts()
    completed = status_counts.get("Completed", 0)
    withdrawn = status_counts.get("Withdrawn", 0)
    terminated = status_counts.get("Terminated", 0)

    denom = completed + withdrawn + terminated + 1e-6
    df["CompletedRatio"] = completed / denom
    return df
