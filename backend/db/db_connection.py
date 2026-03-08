import sqlite3
import pandas as pd

conn = sqlite3.connect("options_data.db")

df = pd.read_csv("backend/data/2026-02-17_exp.csv")

df.to_sql("options_data", conn, if_exists="replace", index=False)

conn.close()