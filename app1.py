
import streamlit as st
import os
import pandas as pd
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from dotenv import load_dotenv
load_dotenv()
from src.fetch_trial import get_trials
from src.clean_data import clean_trials
from src.score_sites import compute_scores
from src.aggregate_sites import normalize_sites
from src.metrics import compute_match_score, compute_data_quality, compute_performance_metrics
from src.database import save_to_sqlite
from src.visualize import plot_distribution, plot_top_sites, plot_top_sites_by_study_count
from utils.logger import log 
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="Clinical Trial Dashboard", layout="wide", page_icon="🧬")
st.title("🧬 Clinical Trial Analytics Dashboard")
st.caption("Analyze trial sites, quality, and performance from ClinicalTrials.gov data")

# ----------------------------
# Sidebar Input
# ----------------------------
st.sidebar.header("⚙️ Data Settings")
term = st.sidebar.text_input("Search Condition / Disease", "dengue")
page_size = st.sidebar.slider("Number of trials to fetch", 10, 100, 50)
run_button = st.sidebar.button("🚀 Run Analysis")

# ----------------------------
# Fetch & Process Data
# ----------------------------
if run_button:
    with st.spinner("Fetching data from ClinicalTrials.gov..."):
        raw_df = get_trials(term, page_size)
        st.session_state.raw_df = raw_df

    with st.spinner("Cleaning and scoring data..."):
        cleaned = clean_trials(raw_df)
        cleaned = compute_match_score(cleaned)
        cleaned = compute_data_quality(cleaned)
        cleaned = compute_performance_metrics(cleaned)
        cleaned = compute_scores(cleaned)
        site_summary = normalize_sites(cleaned)

        st.session_state.cleaned = cleaned
        st.session_state.site_summary = site_summary
        save_to_sqlite(cleaned, f"{term.lower()}_clinical_sites.db")

    st.success(f"✅ Data fetched and processed successfully for '{term}'")
# ----------------------------
# 🧠 Chat Agent Tab
# ----------------------------
# ----------------------------
# Display Layout After Data Load
# ----------------------------
if "cleaned" in st.session_state:
    cleaned = st.session_state.cleaned
    site_summary = st.session_state.site_summary

    # ----------------------------
    # 🧠 Toggle Chatbot Panel
    # ----------------------------
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False

    st.markdown("### ⚙️ Control Panel")
    toggle_col1, toggle_col2 = st.columns([0.9, 0.1])
    with toggle_col2:
        if st.button("🧠 Open Chat Assistant" if not st.session_state.show_chat else "❌ Close Chat"):
            st.session_state.show_chat = not st.session_state.show_chat

    # ----------------------------
    # Layout Adjusts Dynamically
    # ----------------------------
    if st.session_state.show_chat:
        left_col, main_col, right_col = st.columns([0.1, 0.65, 0.25])
    else:
        left_col, main_col = st.columns([0.1, 0.9])
        right_col = None

    # ----------------------------
    # 💬 Right Column - Chatbot Agent (Collapsible)
    # ----------------------------
    if right_col:
        with right_col:
            st.markdown("### 💬 Data Agent")
            st.caption("Ask questions about trials or site data.")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            choice = st.radio("Query dataset:", ["Trials", "Sites"], key="dataset_choice")
            user_question = st.text_input("Enter your question:", key="chat_input")

            if user_question:
                with st.spinner("Analyzing..."):
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash-lite",
                        temperature=0.0,
                        max_output_tokens=1024
                    )
                    df_to_query = cleaned if choice == "Trials" else site_summary
                    prefix_text = (
"You are a data analysis expert working with a Pandas DataFrame named df. "
    "When you need to inspect data, use expressions directly (like df['col'].unique() or df.head()), "
    "NOT print() statements. Do not use Markdown code fences or ```python blocks. "
    "Always compute answers from the DataFrame and then explain the result clearly."
    if choice == "Trials"
    else
    "You are a data analysis expert working with a Pandas DataFrame named df. "
    "Do NOT use print(), and do NOT wrap code in ```python blocks. "
    "Use direct expressions like df.describe(), df['column'].value_counts(), etc. "
    "Always compute answers exactly, then explain concisely."
)

                    agent = create_pandas_dataframe_agent(
                        llm,
                        df_to_query,
                        verbose=True,
                        allow_dangerous_code=True,
                        number_of_head_rows=0,
                        prefix=prefix_text
                    )

                    try:
                        answer = agent.run(user_question)
                        st.session_state.chat_history.append((user_question, answer))
                    except Exception as e:
                        answer = f"Error: {e}"
                        st.session_state.chat_history.append((user_question, answer))

            # Display conversation
            for q, a in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.markdown(f"**You:** {q}")
                with st.chat_message("assistant"):
                    st.markdown(f"{a}")

            if st.button("🧹 Clear Chat"):
                st.session_state.chat_history = []

    # ----------------------------
    # 🏠 Main Dashboard Tabs
    # ----------------------------
    with main_col:
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Overview", "🏥 Sites", "📊 Metrics", "📄 Data"])

        # ---- Overview Tab ----
        with tab1:
            st.subheader("📈 Summary Overview")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Trials", len(cleaned))
            col2.metric("Unique Sites", len(site_summary))
            col3.metric("Avg. Composite Score", f"{cleaned['score_pct'].mean():.2f}")

            st.markdown("---")
            st.write("### 🧠 Key Insights")
            st.write("""
            - **Top-performing sites** indicate operational excellence.  
            - **High data quality** suggests reliable reporting.  
            - **Low performance** may signal recruitment or management gaps.
            """)

            fig1 = plot_top_sites(cleaned, n=10)
            st.pyplot(fig1)

            fig2 = plot_distribution(cleaned)
            st.pyplot(fig2)

        # ---- Sites Tab ----
        with tab2:
            st.subheader("🏥 Site-Level Performance")
            col1, col2 = st.columns(2)
            with col1:
                fig3 = plot_top_sites_by_study_count(site_summary)
                st.pyplot(fig3)
            with col2:
                st.dataframe(site_summary.head(20), use_container_width=True)

            st.download_button(
                label="⬇️ Download Site Summary (CSV)",
                data=site_summary.to_csv(index=False),
                file_name=f"{term}_site_summary.csv",
                mime="text/csv"
            )

        # ---- Metrics Tab ----
        with tab3:
            st.subheader("📊 Quality & Performance Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Mean Match Score", f"{cleaned['MatchScore'].mean():.2f}")
            col2.metric("Mean Data Quality", f"{cleaned['DataQuality'].mean():.2f}")
            col3.metric("Mean Performance", f"{cleaned['score_pct'].mean():.2f}")

            min_score = st.slider("Filter trials above score (%)", 0, 100, 60)
            filtered = cleaned[cleaned["score_pct"] >= min_score]
            st.dataframe(filtered.head(20), use_container_width=True)

            st.download_button(
                label="⬇️ Download Filtered Trials (CSV)",
                data=filtered.to_csv(index=False),
                file_name=f"{term}_filtered_trials.csv",
                mime="text/csv"
            )

        # ---- Data Tab ----
        with tab4:
            st.subheader("📄 Raw & Cleaned Data Views")
            with st.expander("Raw Data"):
                st.dataframe(st.session_state.raw_df.head(20), use_container_width=True)
            with st.expander("Cleaned Data"):
                st.dataframe(cleaned.head(20), use_container_width=True)

            st.download_button(
                label="⬇️ Download Cleaned Dataset (CSV)",
                data=cleaned.to_csv(index=False),
                file_name=f"{term}_cleaned_data.csv",
                mime="text/csv"
            )
