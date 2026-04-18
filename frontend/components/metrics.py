import streamlit as st

def show_metrics(df):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Contracts", len(df))

    with col2:
        st.metric("Avg Price", round(df["price"].mean(),2))

    with col3:
        st.metric("Total Volume", int(df["volume"].sum()))
