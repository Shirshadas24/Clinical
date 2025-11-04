# Clinical Trial Analytics Dashboard
## Objective

The Clinical Trial Analytics Dashboard is designed to simplify and automate the analysis of clinical trial data sourced from ClinicalTrials.gov.
It aggregates study-level information, evaluates trial sites based on data quality, enrollment, and recency, and visualizes site-level and study-level performance.
The goal is to assist researchers, regulators, and sponsors in identifying top-performing sites, improving operational planning, and ensuring high-quality, up-to-date data reporting.

## Dataset Used

- Source: ClinicalTrials.gov API v2
- Data Type: JSON (converted to structured tabular format using pandas)
- Fields Extracted:
    - NCT ID, Title, Condition
    - Enrollment Count
    - Start & Last Update Dates
    - Location / Lead Sponsor Name
    - Study Type and Status

Each API query fetches up to a selected number of trials (default: 50) for a given medical condition (e.g., “dengue”).

# Data Preprocessing Steps

1. Data Fetching:
    - The API is queried using the selected condition (e.g., “dengue”).
    - Only valid studies with structured data are retained.

2. Cleaning (clean_trials.py):
    - Dropped all-NaN columns and standardized column names.
    - Filled missing Location values with "Unknown".
    - Converted list/dict fields to strings and removed duplicates.

3. Aggregation (aggregate_sites.py):
    - Sites grouped by Location or LeadSponsorName.
    - Calculated average enrollment and total studies per site.

4. Scoring (score_sites.py):
    - Computed weighted composite score (0–100) using:
- Completeness (40%), Enrollment (30%), Recency (30%)

5. Quality & Metrics (metrics.py):
   - DataQuality = completeness × recency weight
   - MatchScore = simulated condition fit
   - CompletedRatio = proportion of completed vs withdrawn trials

6.Persistence (database.py):
- Cleaned dataset stored in SQLite for reproducibility.

# Key Visualizations & Insights
Visualization	Description
```
 Top Trials Bar Chart	        | Displays top 10 trials by composite score.
 Score Distribution Histogram	| Shows how scores are spread across all studies.
 Top Sites Chart	            | Highlights leading research sites or sponsors based on total study count.
 Filtered Metrics Table	        | Allows users to explore trials above a chosen performance threshold.
```
## Insights:
- Sites with consistent updates and higher enrollments achieve better scores.
- “Unknown” locations often correlate with incomplete reporting.
- Data quality and match scores can guide regulatory oversight and future trial site selection.

## Tech Stack
```
### Layer	       ### Tools & Frameworks
Frontend	       Streamlit (for interactive dashboard)
Backend / Logic	   Python 3, Pandas, NumPy
Data Fetching	   ClinicalTrials.gov API v2
Visualization	   Matplotlib
AI Assistant	   LangChain + Gemini (Google Generative AI)
Database	       SQLite
Environment	       .env for secure API configuration
```
## Real-World Impact
- For Researchers: Quickly identify promising and reliable sites for collaboration.
- For Sponsors: Evaluate site performance and plan efficient multi-site trials.
- For Regulators: Monitor data transparency, update frequency, and study quality.
- For Public Health Agencies: Gain insights into ongoing clinical research across diseases and geographies.
  
This dashboard streamlines evidence-based decision-making in biomedical research by combining automation, data analytics, and generative AI.

## How to Run Locally
```
# 1️⃣ Clone the repo
git clone <your-repo-url>
cd clinical-trial-dashboard

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the app
streamlit run app.py
```

Then open the local URL shown in the terminal to access the dashboard.
