# utils/logger.py
import streamlit as st

def log(msg):
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append(msg)
    print(msg)  
