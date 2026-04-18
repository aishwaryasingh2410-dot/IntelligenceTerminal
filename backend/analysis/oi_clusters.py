from typing import Dict, List

import pandas as pd


def _normalized_df(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.rename(columns={"oi_ce": "oi_CE", "oi_pe": "oi_PE"}).copy()
    normalized["strike"] = pd.to_numeric(normalized.get("strike"), errors="coerce")
    normalized["oi_CE"] = pd.to_numeric(normalized.get("oi_CE"), errors="coerce").fillna(0)
    normalized["oi_PE"] = pd.to_numeric(normalized.get("oi_PE"), errors="coerce").fillna(0)
    return normalized.dropna(subset=["strike"])


def calculate_top_oi_strikes(df: pd.DataFrame, limit: int = 10) -> List[Dict]:
    if df.empty:
        return []

    grouped = (
        _normalized_df(df)
        .assign(total_oi=lambda x: x["oi_CE"] + x["oi_PE"])
        .groupby("strike", as_index=False)["total_oi"]
        .sum()
        .sort_values("total_oi", ascending=False)
        .head(limit)
    )

    return [
        {"strike": float(row["strike"]), "total_oi": float(row["total_oi"])}
        for _, row in grouped.iterrows()
    ]


def summarize_call_put_oi(df: pd.DataFrame) -> Dict[str, float]:
    normalized = _normalized_df(df)
    return {
        "call_oi": float(normalized["oi_CE"].sum()),
        "put_oi": float(normalized["oi_PE"].sum()),
    }
