import streamlit as st
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_all_data

st.title("🌐 Volatility Surface")

df = load_all_data()
if df.empty:
    st.warning("No data available.")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

for col in ["strike", "expiry", "ce"]:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

try:
    pivot = df.pivot_table(values="ce", index="strike", columns="expiry", aggfunc="mean")
except Exception as e:
    st.error(f"Could not create volatility surface: {e}")
    st.stop()

if pivot.empty:
    st.warning("Pivot table is empty.")
    st.stop()

st.subheader("📊 Strike vs Expiry Volatility Surface")
fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Turbo",
                template="plotly_dark", title="Volatility Surface (Strike vs Expiry)")
fig.update_layout(xaxis_title="Expiry", yaxis_title="Strike Price")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📈 CE Price Distribution")
fig2 = px.histogram(df, x="ce", nbins=40, template="plotly_dark", title="Distribution of CE Prices")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📋 Data Preview")
st.dataframe(df.head(50), use_container_width=True)