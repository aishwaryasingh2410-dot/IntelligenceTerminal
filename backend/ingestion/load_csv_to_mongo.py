import os
from pathlib import Path

import pandas as pd

from backend.db.connection import raw_options_collection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FOLDER = PROJECT_ROOT / "data"


def load_csvs_to_mongo() -> int:
    files = sorted(file for file in os.listdir(DATA_FOLDER) if file.endswith(".csv"))
    total_records = 0

    for file in files:
        path = DATA_FOLDER / file
        print(f"Loading {file}...")

        df = pd.read_csv(path)
        records = df.to_dict("records")

        if records:
            raw_options_collection.insert_many(records)
            total_records += len(records)

    print(f"\nInserted {total_records} records into MongoDB collection 'raw_options_chain'")
    return total_records


if __name__ == "__main__":
    load_csvs_to_mongo()
