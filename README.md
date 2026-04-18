# Team Rocket: AI-Powered Options Market Analytics with Cursor-Optimized Processing

## Overview

This project is a comprehensive AI-powered analytics platform for options market data, developed as part of a hackathon challenge. It processes large-scale options chain data to extract meaningful insights, detect anomalies, and provide interactive visualizations.

The system is designed to handle high-frequency options data across multiple dimensions including time, strike prices, expiries, trading volume, and open interest. By using cursor-optimized database processing, it efficiently manages large datasets while providing real-time analytics.

## Features

- **Data Ingestion & Processing**: Automated loading of options data into MongoDB with optimized cursor-based queries
- **Market Analytics**: Calculation of key metrics like Put-Call Ratio (PCR), Max Pain, Open Interest concentration
- **Anomaly Detection**: AI-driven identification of unusual market activity
- **Interactive Dashboards**: Multiple visualization interfaces (Streamlit frontend, React dashboard, Node.js server)
- **Performance Optimization**: Cursor-based database access for efficient large-scale data handling
- **Real-time Processing**: Live data feed integration for continuous market monitoring

## Architecture

The project follows a modular architecture:

- **Backend (Python)**: Core analytics engine with MongoDB integration
- **Frontend (Streamlit)**: Interactive web interface for data exploration
- **Dashboard (React)**: Advanced visualization dashboard
- **Server (Node.js)**: API server for data serving
- **Database (MongoDB)**: Document-based storage with optimized indexing

## Dashboard Interfaces

### Streamlit Frontend

The Streamlit frontend is designed for rapid interactive analysis and quick prototyping. It is ideal for exploring raw market data, filtering by expiry and strike, and viewing analytics like PCR, anomaly alerts, and database performance results in a simple, responsive interface.

### React Dashboard

The React dashboard is the polished analytics layer for business-ready presentation and advanced visual storytelling. It highlights trends, performance benchmarking, market signals, and live-style analytics in a more immersive, presentation-ready layout.

These two dashboard layers together support both fast iteration and final delivery: Streamlit for quick analytics exploration, and React for a refined dashboard experience.

## Project Structure

```
├── backend/                 # Python backend with analytics modules
│   ├── analysis/           # Market analysis algorithms
│   ├── db/                 # Database connection and optimization
│   ├── api/                # FastAPI routes
│   └── pipelines/          # Data processing pipelines
├── frontend/               # Streamlit web application
│   ├── pages/             # Individual analysis pages
│   └── components/        # Reusable UI components
├── dashboard/              # React-based dashboard
├── server/                 # Node.js API server
├── data/                   # Sample datasets
├── notebooks/              # Jupyter notebooks for analysis
├── docs/                   # Documentation
└── submission/             # Final project deliverables
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aishwaryasingh2410-dot/team-rocket.git
   cd team-rocket
   ```

2. **Set up Python environment**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MongoDB**
   - Set up MongoDB instance
   - Create `.env` file with `MONGO_URI` (see `.env.example`)

4. **Install Node.js dependencies**
   ```bash
   cd server && npm install
   cd ../dashboard && npm install
   ```

### Running the Application

1. **Start the backend**
   ```bash
   cd backend
   python -m uvicorn api.main:app --reload
   ```

2. **Start the Streamlit frontend**
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. **Start the React dashboard**
   ```bash
   cd dashboard
   npm start
   ```

4. **Start the Node.js server**
   ```bash
   cd server
   npm start
   ```

## Screenshots

Add your dashboard screenshot files into a folder named `docs/screenshots` and update the file names below if needed.

### Dashboard Overview

![Dashboard Overview](docs/screenshots/dashboard_overview.png)

A high-level view of the dashboard showing the key market indicators, total open interest, total volume, and PCR.

### Performance Benchmark

![Performance Benchmark](docs/screenshots/database_performance.png)

MongoDB query performance comparisons for normal vs cursor-optimized data access.

### Intelligence Terminal

![Intelligence Terminal](docs/screenshots/intelligence_terminal.png)

Interactive analysis and metrics display for the options market intelligence terminal.

## Key Analytics

- **Put-Call Ratio (PCR)**: Sentiment indicator based on open interest
- **Max Pain**: Strike price with maximum expiring options value
- **Open Interest Clusters**: Concentration analysis across strikes
- **Anomaly Detection**: Statistical identification of unusual activity
- **Volatility Analysis**: Smile and surface calculations

## Dataset

The project uses options chain data with the following structure:

| Field | Description |
|-------|-------------|
| datetime | Timestamp |
| expiry | Option expiry date |
| strike | Strike price |
| spot_close | Underlying price |
| oi_CE | Call open interest |
| oi_PE | Put open interest |
| volume_CE | Call volume |
| volume_PE | Put volume |

## Development

The project was developed using:
- **Python** for data processing and analytics
- **MongoDB** for data storage
- **Streamlit** for rapid prototyping
- **React** for advanced dashboards
- **Node.js** for API services

## Team

Developed by Team Rocket for the a Hackathon Challenge.

## License

This project is developed for educational and demonstration purposes.

The goal is to transform raw derivatives data into **actionable insights for traders and analysts**.

---

## Use of Free and Open Source Software (FOSS)

A core objective of this event is to promote the use of **Free and Open Source Software (FOSS)**.

Participants will be **significantly evaluated based on how effectively they use FOSS tools and frameworks in their solution**.

Examples of recommended open-source technologies include:

### Data Analysis
- Python
- Pandas
- NumPy

### Machine Learning
- Scikit-learn
- PyTorch
- TensorFlow

### Visualization
- Plotly
- Matplotlib
- D3.js

### Dashboard Development
- Streamlit
- Dash
- React

### Data Infrastructure
- PostgreSQL
- DuckDB
- Apache Spark

Teams that creatively leverage open-source ecosystems or build reusable open tools will receive additional consideration during evaluation.

---

## Evaluation Criteria

Submissions will be evaluated based on the following factors:

### Visualization Quality
Clarity and effectiveness of visualizations in representing complex options data.

### Analytical Depth
Ability to uncover meaningful patterns in volatility, trading activity, or market structure.

### AI / Machine Learning Integration
Use of intelligent models for pattern detection, forecasting, or anomaly detection.

### Scalability
Ability to handle large datasets efficiently.

### User Experience
Ease of use, interactivity, and usability of the platform.

### Use of FOSS Tools
Effective and innovative use of open-source technologies.

### Innovation
Originality in analytics techniques, visualization design, or platform features.

---

## Submission Guidelines

Each team submission should include:

- Source code
- Documentation explaining the approach
- Instructions for running the solution
- Any trained models or additional data processing scripts

---

## Final Note

The purpose of this challenge is not only to build visual dashboards but to **extract meaningful insights from complex options market data using analytics and AI**.

Participants are encouraged to experiment, explore new ideas, and build innovative solutions that improve understanding of derivatives markets.

Good luck and happy building.
