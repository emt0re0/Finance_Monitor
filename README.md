# 🚀 Global Finance Monitor (Serverless)

A personal finance dashboard powered by **GitHub Actions** (Data ETL), **GitHub Pages** (Hosting), and **Akshare** (Data Source).

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Preview)

## ✨ Features

- **Multi-Market Tracking**: Real-time data for **S&P 500**, **Nasdaq**, **A-Share (CSI 300/SSE)**, **Hang Seng**, **Gold**, and **Bitcoin**.
- **Quant Screener**: Daily automated scanning of top gainers in the A-Share market.
- **DCA Simulator**: Built-in backtesting to show returns for Dollar-Cost Averaging strategies (Daily Investment).
- **Serverless Architecture**: 100% free hosting and compute using GitHub infrastructure.
- **Resilient Data**: Uses `Akshare` (Sina Finance API) for reliable access globally (including China).

## 🛠️ Technology Stack

- **Backend**: Python 3.9+
    - `akshare`: Financial data fetching.
    - `pandas`: Data processing.
- **Frontend**: Static HTML5
    - `Tailwind CSS`: Utility-first styling.
    - `Apache ECharts`: Interactive financial charts.
    - `Marked.js`: Markdown rendering for reports.
- **Automation**: GitHub Actions (Cron Job: Daily at 21:00 UTC).

## 🚀 Deployment Guide

### 1. Fork this Repository
Click the **Fork** button at the top right to create your own copy.

### 2. Enable GitHub Pages
1. Go to your repository **Settings**.
2. Click on **Pages** in the left sidebar.
3. Under **Build and deployment > Source**, select **Deploy from a branch**.
4. Select the **main** branch and `/ (root)` folder.
5. Click **Save**.

### 3. Activate Automation
1. Go to the **Actions** tab.
2. You might see a warning "Workflows aren't being run on this forked repository". Click **I understand my workflows, go ahead and enable them**.
3. Select **Daily Finance Update** on the left.
4. Click **Run workflow** -> **Run workflow** to trigger the first data fetch manually.
5. Wait for the green checkmark ✅ (approx. 1-2 mins).

### 4. Visit Your Dashboard
Once the workflow finishes, your site will be live at:
`https://<your-username>.github.io/<repository-name>/`

*(Note: It might take a few minutes for the first deploy to propagate).*

## 📂 Project Structure

```text
.
├── .github/workflows/   # Daily cron job configuration
├── data/                # Generated JSON data (Do not edit manually)
├── scripts/             # Python backend logic
│   ├── fetch_data.py    # Fetches market index data
│   └── screener.py      # Generates quant reports & DCA stats
├── js/                  # Frontend logic
├── index.html           # Dashboard UI
└── requirements.txt     # Dependencies
```

## 🤝 Contributing
Feel free to open issues or PRs to add more data sources (e.g., individual stocks) or improve the UI!

## 📄 License
MIT