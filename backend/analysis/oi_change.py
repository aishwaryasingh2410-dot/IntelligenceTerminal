from typing import Dict, List

import pandas as pd


def calculate_oi_change_by_strike(df: pd.DataFrame, limit: int = 10) -> List[Dict]:
    if df.empty or "datetime" not in df.columns or "strike" not in df.columns:
        return []

    normalized = df.rename(columns={"oi_ce": "oi_CE", "oi_pe": "oi_PE"}).copy()
    normalized["datetime"] = pd.to_datetime(normalized["datetime"], errors="coerce")
    normalized["strike"] = pd.to_numeric(normalized["strike"], errors="coerce")
    normalized["oi_CE"] = pd.to_numeric(normalized.get("oi_CE"), errors="coerce").fillna(0)
    normalized["oi_PE"] = pd.to_numeric(normalized.get("oi_PE"), errors="coerce").fillna(0)
    normalized = normalized.dropna(subset=["datetime", "strike"])

    if normalized.empty:
        return []

    latest_points = sorted(normalized["datetime"].unique())
    if len(latest_points) < 2:
        return []

    current_time = latest_points[-1]
    previous_time = latest_points[-2]

    current = (
        normalized.loc[normalized["datetime"] == current_time]
        .assign(total_oi=lambda x: x["oi_CE"] + x["oi_PE"])
        .groupby("strike", as_index=False)["total_oi"]
        .sum()
        .rename(columns={"total_oi": "current_total_oi"})
    )
    previous = (
        normalized.loc[normalized["datetime"] == previous_time]
        .assign(total_oi=lambda x: x["oi_CE"] + x["oi_PE"])
        .groupby("strike", as_index=False)["total_oi"]
        .sum()
        .rename(columns={"total_oi": "previous_total_oi"})
    )

    merged = current.merge(previous, on="strike", how="outer").fillna(0)
    merged["oi_change"] = merged["current_total_oi"] - merged["previous_total_oi"]
    merged["abs_change"] = merged["oi_change"].abs()
    merged = merged.sort_values("abs_change", ascending=False).head(limit)

    return [
        {
            "strike": float(row["strike"]),
            "current_total_oi": float(row["current_total_oi"]),
            "previous_total_oi": float(row["previous_total_oi"]),
            "oi_change": float(row["oi_change"]),
        }
        for _, row in merged.iterrows()
    ]
