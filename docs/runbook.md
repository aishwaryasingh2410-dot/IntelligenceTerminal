# CodeForge Runbook

## 1. Load raw CSV data
```bash
python -m backend.ingestion.load_csv_to_mongo
```

This loads local files from `CodeForge/data` into MongoDB collection `raw_options_chain`.

## 2. Create indexes
```bash
python -m backend.db.create_indexes
```

This creates the indexes needed for efficient cursor-based retrieval and analytics lookups.

## 3. Run the incremental analytics pipeline
```bash
python -m backend.pipelines.process_incremental
```

This:
- reads only new records using a cursor
- computes PCR, max pain, top OI, and unusual OI in Python
- stores results in `analytics_snapshots` and `anomaly_signals`
- saves a processing checkpoint for the next run

## 4. Present the project in two parts

### Data Analysis with Python
- show the analytics modules in `backend/analysis/`
- show notebook outputs and derived metrics
- explain how insights are computed from raw options data

### Cursor-Based Optimization
- show the cursor reader in `backend/db/cursor_reader.py`
- show checkpoints in `backend/db/checkpoints.py`
- show indexes in `backend/db/indexes.py`
- explain why batch processing is better than full scans
