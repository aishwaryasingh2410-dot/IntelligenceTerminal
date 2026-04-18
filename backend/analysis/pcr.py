from typing import Dict

import pandas as pd


def _normalize_oi_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [col.strip() for col in normalized.columns]

    rename_map = {}
    if "oi_ce" in normalized.columns and "oi_CE" not in normalized.columns:
        rename_map["oi_ce"] = "oi_CE"
    if "oi_pe" in normalized.columns and "oi_PE" not in normalized.columns:
        rename_map["oi_pe"] = "oi_PE"
    if rename_map:
        normalized = normalized.rename(columns=rename_map)
    return normalized


def calculate_pcr(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {"call_oi": 0.0, "put_oi": 0.0, "pcr": 0.0}

    normalized = _normalize_oi_columns(df)
    call_oi = float(normalized.get("oi_CE", pd.Series(dtype=float)).fillna(0).sum())
    put_oi = float(normalized.get("oi_PE", pd.Series(dtype=float)).fillna(0).sum())
    pcr = 0.0 if call_oi == 0 else put_oi / call_oi
    return {"call_oi": call_oi, "put_oi": put_oi, "pcr": pcr}


def classify_sentiment(pcr: float) -> str:
    if pcr < 0.8:
        return "Bullish"
    if pcr > 1.2:
        return "Bearish"
    return "Neutral"
