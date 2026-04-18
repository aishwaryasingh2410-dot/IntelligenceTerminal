from typing import Dict, Optional

import pandas as pd


def _group_strike_oi(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.rename(columns={"oi_ce": "oi_CE", "oi_pe": "oi_PE"})
        .assign(
            oi_CE=lambda x: pd.to_numeric(x.get("oi_CE"), errors="coerce").fillna(0),
            oi_PE=lambda x: pd.to_numeric(x.get("oi_PE"), errors="coerce").fillna(0),
            strike=lambda x: pd.to_numeric(x.get("strike"), errors="coerce"),
        )
        .dropna(subset=["strike"])
        .groupby("strike", as_index=False)[["oi_CE", "oi_PE"]]
        .sum()
        .sort_values("strike")
    )
    return grouped


def calculate_max_pain(df: pd.DataFrame) -> Dict[str, Optional[float]]:
    if df.empty or "strike" not in df.columns:
        return {"max_pain_strike": None, "pain_value": None}

    grouped = _group_strike_oi(df)
    if grouped.empty:
        return {"max_pain_strike": None, "pain_value": None}

    strikes = grouped.to_dict("records")
    min_pain = float("inf")
    max_pain_strike = None

    for strike_row in strikes:
        strike = strike_row["strike"]
        pain = 0.0
        for option_row in strikes:
            option_strike = option_row["strike"]
            if strike > option_strike:
                pain += (strike - option_strike) * option_row["oi_CE"]
            elif strike < option_strike:
                pain += (option_strike - strike) * option_row["oi_PE"]

        if pain < min_pain:
            min_pain = pain
            max_pain_strike = strike

    return {"max_pain_strike": max_pain_strike, "pain_value": min_pain}
