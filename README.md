# 🚀 Global Finance Monitor (Serverless)

A high-performance, serverless financial dashboard powered by **GitHub Actions (ETL)**, **GitHub Pages (Hosting)**, and **Akshare (Data API)**.

> ⚠️ **Disclaimer**: This project is for educational and technical demonstration purposes only. All data is sourced from public networks. It does **NOT** provide any investment advice. Markets are risky; invest with caution.

## ✨ Key Features

- **Multi-Market Tracking**: Real-time monitoring of S&P 500, Nasdaq, SSE Composite, CSI 300, Hang Seng Index, Gold, and Bitcoin.
- **Value Investing Screener**:
    - **A-Shares**: Filters for "Core Assets" with Market Cap > ¥50B and PE Ratio (0-60).
    - **HK Stocks**: Filters for "Blue Chips" with Price > $5.0 and Turnover > $100M.
    - **US Stocks**: Filters for "Big Tech" with Market Cap > $50B and PE Ratio (0-60).
- **Intelligent DCA Calculator**: Professional Dollar-Cost Averaging simulator with customizable date ranges, frequencies, and investment amounts.
- **Professional Visualizations**: Interactive charts powered by **Apache ECharts**, supporting mouse-wheel zoom, drag-to-pan, and long-term history tracking.
- **Serverless Automation**: 100% automated data pipelines and hosting using GitHub's free infrastructure.

## 🛠️ Technology Stack

- **Backend**: Python 3.9+
    - `akshare`: Comprehensive financial data interface.
    - `pandas`: Data cleansing and incremental storage logic.
- **Frontend**: Modern Static Web
    - `Tailwind CSS`: Responsive utility-first styling.
    - `Apache ECharts`: High-performance financial charting.
    - `Marked.js`: Real-time Markdown rendering for AI/Quant reports.
- **CI/CD**: GitHub Actions (Scheduled Daily at 21:00 UTC).

## 📂 Project Structure

```text
.
├── .github/workflows/   # Automated update workflows
├── data/                # Incremental market data (JSON)
├── scripts/             # Python logic (ETL & Value Screening)
├── js/                  # Frontend logic & ECharts config
├── index.html           # Dashboard User Interface
└── requirements.txt     # Backend dependencies
```

## 🚀 Deployment Guide

### 1. Fork the Repository
Click the **Fork** button at the top right to create your own copy.

### 2. Setup GitHub Pages
1. Go to your repository **Settings**.
2. Click **Pages** in the left sidebar.
3. Under **Build and deployment > Source**, select **Deploy from a branch**.
4. Select the `main` branch and `/ (root)` folder. Click **Save**.

### 3. Trigger Data Pipeline
1. Go to the **Actions** tab.
2. Select **Daily Finance Update** on the left.
3. Click **Run workflow** to manually trigger the first data fetch.
4. Once the workflow turns green (✅), your data is ready.

### 4. Visit Dashboard
Your dashboard will be available at:
`https://<your-username>.github.io/<repository-name>/`

## 📄 License
MIT