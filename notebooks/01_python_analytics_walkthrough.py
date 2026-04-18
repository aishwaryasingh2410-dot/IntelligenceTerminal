import pprint

import pandas as pd

from backend.analysis import (
    calculate_max_pain,
    calculate_oi_change_by_strike,
    calculate_pcr,
    calculate_pcr_timeseries,
    calculate_rolling_pcr_summary,
    calculate_top_oi_strikes,
    detect_unusual_oi,
)
from backend.db.connection import raw_options_collection


def main():
    df = pd.DataFrame(list(raw_options_collection.find({})))
    print("Python Analytics Walkthrough")
    print("=" * 60)
    print(f"Rows loaded: {len(df)}")
    print()

    print("PCR metrics")
    pprint.pp(calculate_pcr(df))
    print()

    print("Rolling PCR summary")
    pprint.pp(calculate_rolling_pcr_summary(df))
    print()

    print("Max pain")
    pprint.pp(calculate_max_pain(df))
    print()

    print("Top OI strikes")
    pprint.pp(calculate_top_oi_strikes(df, limit=5))
    print()

    print("OI change by strike")
    pprint.pp(calculate_oi_change_by_strike(df, limit=5))
    print()

    print("Unusual OI")
    pprint.pp(detect_unusual_oi(df, limit=5))
    print()

    print("PCR timeseries sample")
    pprint.pp(calculate_pcr_timeseries(df, limit=5))


if __name__ == "__main__":
    main()
