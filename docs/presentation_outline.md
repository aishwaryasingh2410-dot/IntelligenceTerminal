# 20-Minute Presentation Outline

## 1. Problem Statement
- Options-chain data is high-volume and multi-dimensional.
- Raw data alone is hard to interpret in real time.
- We need both efficient storage/retrieval and analytical summarization.

## 2. System Architecture
- MongoDB stores raw, processed, and summary data.
- Python performs data cleaning and analytics.
- Node/React visualizes final summaries.

## 3. Cursor-Based Optimization
- Full scan vs cursor-batch retrieval
- Checkpoints in `processing_checkpoints`
- Indexes for `datetime`, `strike`, `expiry`
- Demo scripts:
  - `python -m backend.db.performance_compare`
  - `python verify_collections.py`

## 4. Python Analytics
- PCR and rolling PCR
- Max pain
- Top OI clusters
- OI change by strike
- Unusual OI detection
- Demo script:
  - `python notebooks/01_python_analytics_walkthrough.py`

## 5. Dashboard
- Reads `latest_market_summary`
- Shows top OI, PCR, max pain, and unusual OI
- Uses live `nifty_ticks` for visible movement

## 6. Key Takeaway
- DBMS value: scalable cursor-based processing
- Python value: analytical insight generation
- Combined value: a realistic market intelligence pipeline
