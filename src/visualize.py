
# file: src/visualize.py

from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd


def plot_top_sites(
    df: pd.DataFrame,
    n: int = 10,
    score_col: str = "score_pct",
    title: Optional[str] = None,
):
    
    if score_col not in df.columns:
        raise ValueError(f"{score_col} not found in DataFrame")

    # Sort and take top N
    top = df.sort_values(score_col, ascending=False).head(n)
    if "BriefTitle" in top.columns and "LeadSponsorName" in top.columns:
        labels = (
        top["BriefTitle"].fillna(top["NCTId"]).str.slice(0, 45)
        + " – " + top["LeadSponsorName"].fillna("")
    )
    else:
        labels = top["BriefTitle"].fillna(top["NCTId"]).str.slice(0, 60)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(labels, top[score_col], color="#4B9CD3")
    ax.invert_yaxis()

    for bar in bars:
        ax.text(
        bar.get_width() + 1,
        bar.get_y() + bar.get_height() / 2,
        f"{bar.get_width():.1f}",
        va="center",
        fontsize=9,
    )

    ax.set_xlabel("Composite Score (0–100)", fontsize=11)
    ax.set_ylabel("Clinical Trial", fontsize=11)
    ax.set_title(
        title or f"Top {n} {top['Condition'].iloc[0] if 'Condition' in top.columns else ''} Trials by Score",
        fontsize=14,
        weight="bold",
)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    return fig
    

def plot_distribution(df: pd.DataFrame, col: str = "score_pct", title: Optional[str] = None):
  
    if col not in df.columns:
        raise ValueError(f"{col} not found in DataFrame")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df[col].dropna(), bins=15, edgecolor="black", color="#7CC6FE", alpha=0.8)
    ax.set_xlabel("Composite Score (0–100)", fontsize=11)
    ax.set_ylabel("Number of Trials", fontsize=11)
    ax.set_title(
        title or "Distribution of Clinical Trial Scores",
        fontsize=13,
        weight="bold",
    )
    ax.grid(alpha=0.3, linestyle="--")
    plt.tight_layout()
    return fig

def plot_top_sites_by_study_count(
    site_df: pd.DataFrame,
    n: int = 10,
    title: Optional[str] = "Top Performing Sites (by Study Count)",
):
    
    if "Site" not in site_df.columns or "TotalStudies" not in site_df.columns:
        raise ValueError("Expected columns ['Site', 'TotalStudies'] in DataFrame")

    top_sites = site_df.sort_values("TotalStudies", ascending=False).head(n)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(top_sites["Site"], top_sites["TotalStudies"], color="#5DADE2")
    ax.invert_yaxis()

    # Add numeric labels to bars
    for bar in bars:
        ax.text(
            bar.get_width() + 0.2,
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.0f}",
            va="center",
            fontsize=9,
        )

    ax.set_xlabel("Total Studies", fontsize=11)
    ax.set_ylabel("Site / Sponsor", fontsize=11)
    ax.set_title(title, fontsize=14, weight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    return fig
