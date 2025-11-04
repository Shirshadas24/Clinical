#aggregate_sites.py
import pandas as pd

def normalize_sites(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate trial-level data into site-level summaries.
    Fallback to LeadSponsorName if Location is missing or all 'Unknown'.
    """
    if df.empty:
        print(" Empty DataFrame provided to normalize_sites.")
        return df

    
    if "Location" in df.columns:
        df["Location"] = df["Location"].fillna("Unknown").str.strip()
        unique_locs = df["Location"].nunique()
        only_unknown = (df["Location"].nunique() == 1) and (df["Location"].iloc[0].lower() == "unknown")

        if unique_locs > 1 and not only_unknown:
            group_col = "Location"
        elif "LeadSponsorName" in df.columns:
            group_col = "LeadSponsorName"
            print(" Using 'LeadSponsorName' as site identifier (Location all 'Unknown').")
        else:
            group_col = "Location"
            print(" No LeadSponsorName found, using Location even though all are 'Unknown'.")
    elif "LeadSponsorName" in df.columns:
        group_col = "LeadSponsorName"
        print("using 'LeadSponsorName' as site identifier (Location column missing).")
    else:
        raise ValueError("Neither 'Location' nor 'LeadSponsorName' found in dataframe.")
    for col in ["StartDate", "LastUpdatePostDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Group and summarize
    site_df = (
        df.groupby(group_col)
        .agg({
            "NCTId": "count",
            "EnrollmentCount": "mean",
            "StartDate": "min",
            "LastUpdatePostDate": "max"
        })
        .reset_index()
        .rename(columns={
            group_col: "Site",
            "NCTId": "TotalStudies",
            "EnrollmentCount": "AvgEnrollment"
        })
    )

    site_df = site_df.sort_values("TotalStudies", ascending=False)
    print(f" Aggregated into {len(site_df)} unique sites using '{group_col}'.")
    return site_df
