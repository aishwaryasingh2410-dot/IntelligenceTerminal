# %% [markdown]
# # CodeForge: AI-Powered Options Market Analytics with Cursor-Optimized Processing
# 
# **DAP Project Notebook**
# 
# This notebook presents the analytical workflow for the CodeForge project. It uses options-chain data to derive decision-support metrics such as Put-Call Ratio (PCR), open-interest concentration, max pain, anomaly indicators, and visual summaries of market behavior.

# %% [markdown]
# ## 1. Objectives
# 
# 1. To load and combine raw options-chain datasets into a structured analysis-ready format.
# 2. To compute core market indicators such as Put-Call Ratio and max pain.
# 3. To identify open-interest concentration across strike prices.
# 4. To detect unusual options activity using anomaly-oriented logic.
# 5. To create visualizations that summarize options-market behavior clearly.
# 6. To support the larger DAP project by connecting analytics with database-efficient processing.

# %% [markdown]
# ## 2. Dataset Description
# 
# The project uses three local CSV datasets stored in the `data/` directory. These files contain options-chain records with fields related to time, expiry, strike, open interest, volume, and spot price.
# 
# Important columns used in this notebook include:
# 
# - `datetime`
# - `expiry`
# - `strike`
# - `spot_close`
# - `oi_CE`, `oi_PE`
# - `volume_CE`, `volume_PE`
# - `ATM`
# 
# These attributes support both market analytics and dashboard visualization.

# %%
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 50)

DATA_DIR = Path('data')
files = sorted(DATA_DIR.glob('*.csv'))
files

# %%
df = pd.concat((pd.read_csv(file) for file in files), ignore_index=True)
df.head()

# %%
df.shape

# %% [markdown]
# ## 3. Data Preprocessing
# 
# The raw data is cleaned and normalized before analysis. This includes:
# 
# - converting date fields to datetime format
# - standardizing numeric columns
# - handling missing values
# - deriving total open interest and total volume
# - preparing the dataset for grouped analytics and plotting

# %%
def preprocess_options_data(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    cleaned.columns = [col.strip() for col in cleaned.columns]

    rename_map = {
        'oi_ce': 'oi_CE',
        'oi_pe': 'oi_PE',
        'volume_ce': 'volume_CE',
        'volume_pe': 'volume_PE'
    }
    cleaned = cleaned.rename(columns={k: v for k, v in rename_map.items() if k in cleaned.columns})

    for col in ['datetime', 'expiry']:
        if col in cleaned.columns:
            cleaned[col] = pd.to_datetime(cleaned[col], errors='coerce')

    numeric_cols = [
        'strike', 'spot_close', 'oi_CE', 'oi_PE', 'volume_CE', 'volume_PE', 'ce', 'pe', 'ATM'
    ]
    for col in numeric_cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors='coerce')

    if 'oi_CE' in cleaned.columns and 'oi_PE' in cleaned.columns:
        cleaned['total_oi'] = cleaned['oi_CE'].fillna(0) + cleaned['oi_PE'].fillna(0)

    if 'volume_CE' in cleaned.columns and 'volume_PE' in cleaned.columns:
        cleaned['total_volume'] = cleaned['volume_CE'].fillna(0) + cleaned['volume_PE'].fillna(0)

    return cleaned


clean_df = preprocess_options_data(df)
clean_df.head()

# %%
clean_df[['strike', 'spot_close', 'oi_CE', 'oi_PE', 'volume_CE', 'volume_PE', 'total_oi', 'total_volume']].describe().T

# %% [markdown]
# ## 4. Dataset Summary
# 
# The following cells summarize the number of files, records, expiry dates, and time coverage present in the project dataset.

# %%
summary = {
    'files_used': len(files),
    'total_rows': int(len(clean_df)),
    'unique_expiries': int(clean_df['expiry'].nunique()) if 'expiry' in clean_df.columns else 0,
    'unique_strikes': int(clean_df['strike'].nunique()) if 'strike' in clean_df.columns else 0,
    'start_datetime': clean_df['datetime'].min() if 'datetime' in clean_df.columns else None,
    'end_datetime': clean_df['datetime'].max() if 'datetime' in clean_df.columns else None,
}
pd.DataFrame([summary])

# %% [markdown]
# ## 5. Analytical Functions
# 
# This section implements the core analytical logic used in the project. These metrics are aligned with the CodeForge backend analytics modules and are useful for both academic discussion and business interpretation.

# %%
def calculate_pcr(frame: pd.DataFrame):
    call_oi = float(frame.get('oi_CE', pd.Series(dtype=float)).fillna(0).sum())
    put_oi = float(frame.get('oi_PE', pd.Series(dtype=float)).fillna(0).sum())
    pcr = 0.0 if call_oi == 0 else put_oi / call_oi
    return {'call_oi': call_oi, 'put_oi': put_oi, 'pcr': pcr}


def classify_sentiment(pcr: float) -> str:
    if pcr < 0.8:
        return 'Bullish'
    if pcr > 1.2:
        return 'Bearish'
    return 'Neutral'


def calculate_top_oi_strikes(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    temp = frame[['strike', 'oi_CE', 'oi_PE']].copy()
    temp['strike'] = pd.to_numeric(temp['strike'], errors='coerce')
    temp['oi_CE'] = pd.to_numeric(temp['oi_CE'], errors='coerce').fillna(0)
    temp['oi_PE'] = pd.to_numeric(temp['oi_PE'], errors='coerce').fillna(0)
    temp['total_oi'] = temp['oi_CE'] + temp['oi_PE']
    return (
        temp.dropna(subset=['strike'])
        .groupby('strike', as_index=False)['total_oi']
        .sum()
        .sort_values('total_oi', ascending=False)
        .head(limit)
    )


def calculate_max_pain(frame: pd.DataFrame):
    grouped = (
        frame[['strike', 'oi_CE', 'oi_PE']]
        .copy()
        .assign(
            strike=lambda x: pd.to_numeric(x['strike'], errors='coerce'),
            oi_CE=lambda x: pd.to_numeric(x['oi_CE'], errors='coerce').fillna(0),
            oi_PE=lambda x: pd.to_numeric(x['oi_PE'], errors='coerce').fillna(0),
        )
        .dropna(subset=['strike'])
        .groupby('strike', as_index=False)[['oi_CE', 'oi_PE']]
        .sum()
        .sort_values('strike')
    )

    strikes = grouped.to_dict('records')
    min_pain = float('inf')
    max_pain_strike = None

    for strike_row in strikes:
        strike = strike_row['strike']
        pain = 0.0
        for option_row in strikes:
            option_strike = option_row['strike']
            if strike > option_strike:
                pain += (strike - option_strike) * option_row['oi_CE']
            elif strike < option_strike:
                pain += (option_strike - strike) * option_row['oi_PE']
        if pain < min_pain:
            min_pain = pain
            max_pain_strike = strike

    return {'max_pain_strike': max_pain_strike, 'pain_value': min_pain}


def detect_unusual_oi(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    temp = frame[['strike', 'oi_CE', 'oi_PE']].copy()
    temp['strike'] = pd.to_numeric(temp['strike'], errors='coerce')
    temp['oi_CE'] = pd.to_numeric(temp['oi_CE'], errors='coerce').fillna(0)
    temp['oi_PE'] = pd.to_numeric(temp['oi_PE'], errors='coerce').fillna(0)
    temp['total_oi'] = temp['oi_CE'] + temp['oi_PE']
    grouped = (
        temp.dropna(subset=['strike'])
        .groupby('strike', as_index=False)['total_oi']
        .sum()
        .sort_values('total_oi', ascending=False)
        .head(limit)
    )
    baseline = float(grouped['total_oi'].mean()) if not grouped.empty else 1.0
    grouped['anomaly_score'] = grouped['total_oi'] / baseline
    return grouped


# %% [markdown]
# ## 6. Key Numerical Results

# %%
pcr_result = calculate_pcr(clean_df)
sentiment = classify_sentiment(pcr_result['pcr'])
max_pain_result = calculate_max_pain(clean_df)
top_oi = calculate_top_oi_strikes(clean_df, limit=10)
anomaly_df = detect_unusual_oi(clean_df, limit=10)

results_df = pd.DataFrame([
    {'metric': 'Total Call OI', 'value': round(pcr_result['call_oi'], 2)},
    {'metric': 'Total Put OI', 'value': round(pcr_result['put_oi'], 2)},
    {'metric': 'PCR', 'value': round(pcr_result['pcr'], 4)},
    {'metric': 'Sentiment', 'value': sentiment},
    {'metric': 'Max Pain Strike', 'value': max_pain_result['max_pain_strike']},
])
results_df

# %% [markdown]
# ## 7. Visualization 1: Spot Price Trend
# 
# This chart shows the movement of the underlying spot price over time. It helps establish the market context within which options activity is analyzed.

# %%
spot_df = (
    clean_df[['datetime', 'spot_close']]
    .dropna()
    .sort_values('datetime')
    .drop_duplicates(subset=['datetime'])
)

fig = px.line(
    spot_df,
    x='datetime',
    y='spot_close',
    title='Spot Price Trend Over Time'
)
fig.update_layout(template='plotly_white')
fig.show()

# %% [markdown]
# **Interpretation:** The spot-price trend provides the broader market direction and is useful when comparing price movement with changes in open interest and sentiment.

# %% [markdown]
# ## 8. Visualization 2: Open Interest by Strike
# 
# The following chart highlights strike-wise concentration of total open interest. High open-interest levels often indicate important price zones.

# %%
fig = px.bar(
    top_oi.sort_values('strike'),
    x='strike',
    y='total_oi',
    title='Top Open Interest Strikes'
)
fig.update_layout(template='plotly_white')
fig.show()

top_oi

# %% [markdown]
# **Interpretation:** Strikes with the largest open-interest concentration may act as support or resistance zones and are useful for market positioning analysis.

# %% [markdown]
# ## 9. Visualization 3: Call vs Put Open Interest
# 
# This visualization compares total call and put open interest in the full dataset.

# %%
call_put_df = pd.DataFrame({
    'Type': ['Call OI', 'Put OI'],
    'Value': [pcr_result['call_oi'], pcr_result['put_oi']]
})

fig = px.bar(call_put_df, x='Type', y='Value', color='Type', title='Call vs Put Open Interest')
fig.update_layout(template='plotly_white', showlegend=False)
fig.show()

# %% [markdown]
# **Interpretation:** The balance between call and put open interest contributes directly to PCR and provides a compact view of market sentiment.

# %% [markdown]
# ## 10. Visualization 4: Put-Call Ratio Summary
# 
# PCR is a widely used sentiment indicator in derivatives analysis. Lower PCR values may indicate bullish bias, while higher values can suggest bearish positioning.

# %%
pcr_display = pd.DataFrame({
    'Metric': ['PCR'],
    'Value': [round(pcr_result['pcr'], 4)]
})

fig = px.bar(pcr_display, x='Metric', y='Value', title=f'Put-Call Ratio ({sentiment})', text='Value')
fig.update_layout(template='plotly_white', showlegend=False)
fig.show()

# %% [markdown]
# **Interpretation:** The computed PCR helps classify the market as bullish, bearish, or neutral and is one of the project’s most important summary indicators.

# %% [markdown]
# ## 11. Visualization 5: Volume Heatmap by Strike and Expiry
# 
# A heatmap is used to show how trading activity is distributed across strike prices and expiries.

# %%
heatmap_df = clean_df[['strike', 'expiry', 'total_volume']].dropna().copy()
pivot = heatmap_df.pivot_table(values='total_volume', index='strike', columns='expiry', aggfunc='sum')

fig = px.imshow(
    pivot,
    aspect='auto',
    title='Volume Heatmap Across Strike and Expiry',
    color_continuous_scale='Blues'
)
fig.update_layout(template='plotly_white')
fig.show()

# %% [markdown]
# **Interpretation:** The heatmap highlights activity concentration zones and helps identify the strike-expiry combinations receiving stronger participation.

# %% [markdown]
# ## 12. Visualization 6: Unusual Open Interest Detection
# 
# This chart marks strikes with unusually large open interest based on a simple relative anomaly score.

# %%
fig = px.bar(
    anomaly_df.sort_values('strike'),
    x='strike',
    y='anomaly_score',
    title='Anomaly Score by Strike',
    text='anomaly_score'
)
fig.update_layout(template='plotly_white')
fig.show()

anomaly_df

# %% [markdown]
# **Interpretation:** Higher anomaly scores indicate unusually strong open-interest accumulation relative to the shortlisted baseline and may represent noteworthy market activity.

# %% [markdown]
# ## 13. Max Pain Result
# 
# Max pain is the strike at which cumulative option-writer payout pressure is minimized based on grouped open-interest values.

# %%
pd.DataFrame([max_pain_result])

# %% [markdown]
# **Interpretation:** The max pain strike gives a compact estimate of the strike around which expiry-side positioning is concentrated.

# %% [markdown]
# ## 14. Discussion
# 
# The notebook shows that raw options-chain data can be transformed into meaningful and decision-supportive metrics. PCR captures directional sentiment, top OI strikes indicate concentration zones, max pain provides an expiry-oriented summary, and anomaly scores help flag unusual positions. Combined with visual analytics, these outputs make complex derivatives data easier to interpret.

# %% [markdown]
# ## 15. Conclusion
# 
# This notebook forms the analytical component of the CodeForge DAP project. It demonstrates how options data can be cleaned, summarized, visualized, and interpreted using Python-based workflows. The outputs generated here can be reused directly in the final report, presentation, and cognitive report.

# %% [markdown]
# ## 16. Export Notes
# 
# Before exporting this notebook to PDF:
# 
# - run all cells
# - keep the chart outputs visible
# - ensure figure screenshots are readable
# - if required by faculty, add a short references section at the end using IEEE citation style


