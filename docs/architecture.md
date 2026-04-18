# Team Rocket Architecture

## Overview
Team Rocket is a hybrid market-intelligence project designed to satisfy two goals at the same time:

1. Data Analysis with Python
2. Advanced Database Management with cursor-based optimization

The project keeps MongoDB as the operational store for raw and processed data, while Python owns the analytical pipeline and insight generation.

## Layers

### Database Layer
- `raw_options_chain`: raw options records from CSV or live ingestion
- `options_chain`: legacy collection kept for compatibility
- `nifty_ticks`: live NIFTY tick data
- `analytics_snapshots`: computed PCR, max pain, OI summaries
- `anomaly_signals`: unusual activity results
- `processing_checkpoints`: last processed cursor values

### Cursor Optimization Layer
- incremental reads using `_id` or `datetime`
- batch-based processing instead of full collection scans
- checkpoint-based resume support
- compound indexes for common filters like `expiry`, `strike`, and `datetime`

### Python Analytics Layer
- PCR and sentiment
- max pain
- top OI clustering
- unusual OI detection
- reusable functions in `backend/analysis/`

### Presentation Layer
- React dashboard reads precomputed analytics instead of owning the calculations
- later this can be replaced or complemented with Streamlit or notebooks

## Processing Flow
1. Ingest raw records into MongoDB.
2. Read only new records through the cursor reader.
3. Compute analytics in Python.
4. Persist summaries into analytics collections.
5. Track progress with checkpoints.
6. Serve or visualize the processed results.

## Subject Mapping

### Data Analysis with Python
- data cleaning with `pandas`
- feature engineering
- trend analytics
- anomaly detection
- notebook-ready outputs

### Advanced Database Management
- cursor-based incremental retrieval
- indexed access patterns
- memory-efficient batching
- resumable pipelines through checkpoints
