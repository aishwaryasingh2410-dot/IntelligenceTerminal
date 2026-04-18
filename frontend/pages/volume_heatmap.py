import streamlit as st
import plotly.express as px
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.data_loader import load_expiry_data, filter_strike_range

st.title("🔥 Options Volume Heatmap")

expiry = st.session_state.get("expiry")
strike_range = st.session_state.get("strike_range")

if expiry is None:
    st.warning("Please select expiry from the main dashboard.")
    st.stop()

df = load_expiry_data(expiry)
if strike_range:
    df = filter_strike_range(df, strike_range[0], strike_range[1])
if df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

temp = df.copy()
temp.columns = temp.columns.str.strip().str.lower()

# normalize column names (handle volume_CE vs volume_ce)
col_map = {c: c.lower() for c in temp.columns}
temp.rename(columns=col_map, inplace=True)

for col in ["strike", "expiry", "datetime", "volume_ce", "volume_pe"]:
    if col not in temp.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

temp["total_volume"] = temp["volume_ce"].fillna(0) + temp["volume_pe"].fillna(0)

st.subheader("📊 Volume Heatmap (Strike vs Expiry)")
try:
    pivot = temp.pivot_table(values="total_volume", index="strike", columns="expiry", aggfunc="sum")
    fig = px.imshow(pivot, color_continuous_scale="Turbo", aspect="auto", template="plotly_dark")
    fig.update_layout(xaxis_title="Expiry", yaxis_title="Strike Price")
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error creating pivot table: {e}")

st.subheader("⏱ Volume Heatmap (Strike vs Time)")
try:
    time_pivot = temp.pivot_table(values="total_volume", index="strike", columns="datetime", aggfunc="sum")
    fig2 = px.imshow(time_pivot, color_continuous_scale="Turbo", aspect="auto", template="plotly_dark")
    fig2.update_layout(xaxis_title="Time", yaxis_title="Strike")
    st.plotly_chart(fig2, use_container_width=True)
except Exception as e:
    st.error(f"Error creating time pivot: {e}")

st.subheader("📊 Call vs Put Volume")
volume_group = temp.groupby("strike")[["volume_ce", "volume_pe"]].sum().reset_index()
fig3 = px.bar(volume_group, x="strike", y=["volume_ce", "volume_pe"],
              barmode="group", title="Call vs Put Volume by Strike", template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("🚨 Volume Spike Detection")
threshold = temp["total_volume"].quantile(0.98)
spikes = temp[temp["total_volume"] > threshold]
if not spikes.empty:
    st.dataframe(spikes.head(20), use_container_width=True)
else:
    st.success("No significant volume spikes detected")

st.subheader("📋 Data Preview")
st.dataframe(temp.head(50), use_container_width=True)
