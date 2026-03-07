import streamlit as st
import pandas as pd
import glob
import plotly.express as px
st.set_page_config(
    page_title="Options Intelligence Terminal",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #161B22;
}

h1,h2,h3,h4 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-container {
    background-color: #161B22;
    border-radius: 10px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(layout="wide")

st.title("📊 Volatility Smile")

files = glob.glob("data/*.csv")

df = pd.concat([pd.read_csv(file) for file in files])

df.columns = df.columns.str.strip()
df.columns = df.columns.str.lower()

iv = df.groupby("strike")["ce"].mean().reset_index()

fig = px.line(
    iv,
    x="strike",
    y="ce",
    markers=True,
    template="plotly_dark",
    title="Volatility Smile (Using CE Price)"
)

st.plotly_chart(fig, use_container_width=True)