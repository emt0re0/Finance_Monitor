# Serverless Finance Monitor - Development Plan

这是一个基于 GitHub Actions (ETL) + GitHub Pages (Hosting) + Gemini API (Analysis) 的无服务器金融监控项目。

## 📅 项目里程碑

### Phase 1: 基础设施与数据引擎 (Infrastructure & Data Engine)
- [ ] **1.1 环境初始化**: 建立项目目录结构，配置 `.gitignore` 和 Python 依赖管理 (`requirements.txt`)。
- [ ] **1.2 核心抓取脚本 (`fetch_data.py`)**: 
    - 集成 `yfinance` 获取 A股/美股/港股/Crypto 历史数据。
    - 实现 DCA (定投) 计算逻辑 (每日/每周/每月收益回测)。
    - 数据清洗与标准化，输出 JSON 格式。
- [ ] **1.3 本地测试**: 确保 Python 脚本在本地运行无误，生成 `data/*.json`。

### Phase 2: 自动化工作流 (Automation - GitHub Actions)
- [ ] **2.1配置 Workflow (`daily_update.yml`)**:
    - 设置定时任务 (Cron Job) 每日收盘后运行。
    - 配置 Python 环境与依赖缓存。
- [ ] **2.2 自动提交机制**:
    - 配置 `GITHUB_TOKEN` 权限。
    - 实现脚本自动 `git commit` & `git push` 生成的 JSON 数据回仓库。

### Phase 3: 前端可视化 (Frontend Dashboard)
- [ ] **3.1 UI 框架搭建**:
    - 创建 `index.html`。
    - 引入 Tailwind CSS (CDN) 进行快速布局。
    - 引入 ECharts 或 Chart.js (CDN) 用于绘图。
- [ ] **3.2 数据对接**:
    - 编写 `app.js` 使用 `fetch()` 读取 Phase 1 生成的 JSON 文件。
- [ ] **3.3 核心图表实现**:
    - 多市场走势概览 (Line Chart)。
    - DCA 收益率对比图 (Bar/Line Chart)。

### Phase 4: AI 价值发现 (AI Integration)
- [ ] **4.1 选股策略脚本 (`screener.py`)**:
    - 编写简单的量化规则 (如: 低 PE, 高 ROE, 均线突破) 筛选 3-5 只潜力股。
- [ ] **4.2 Gemini API 集成**:
    - 申请并配置 Google Gemini API Key 到 GitHub Secrets。
    - 设计 Prompt：传入股票基础数据，要求 AI 生成简报。
- [ ] **4.3 展示集成**: 将 AI 生成的 Markdown/Text 报告展示在前端页面。

### Phase 5: 扩展与优化 (Extensions & Polish)
- [ ] **5.1 移动端适配 (PWA)**: 添加 `manifest.json` 和 meta 标签。
- [ ] **5.2 恐慌贪婪指数**: 集成相关 API (如 CNN Money 或 Alternative.me)。
- [ ] **5.3 资产相关性分析**: 计算 Pearson 相关系数并可视化。

---

## 📂 推荐目录结构

```text
.
├── .github/
│   └── workflows/
│       └── daily_update.yml  # 自动化流程
├── data/                     # 存放生成的 JSON 数据 (由 Action 自动写入)
│   ├── market_summary.json
│   ├── dca_simulation.json
│   └── ai_report.json
├── scripts/                  # Python 后端脚本
│   ├── fetch_data.py         # 市场数据抓取
│   ├── dca_calculator.py     # 定投计算逻辑
│   └── ai_analyst.py         # Gemini 分析与选股
├── index.html                # 主页
├── css/                      # 自定义样式 (如果 Tailwind 不够用)
├── js/                       # 前端逻辑
│   ├── main.js
│   └── charts.js
├── requirements.txt          # Python 依赖
└── README.md
```

## 🛠 技术栈清单
*   **Backend**: Python 3.9+
    *   `yfinance`: 雅虎财经数据接口
    *   `pandas`: 数据处理
    *   `google-generativeai`: Gemini API SDK
*   **Frontend**: Static HTML
    *   `Tailwind CSS`: 样式 (CDN引入)
    *   `Apache ECharts`: 专业金融图表 (CDN引入)
    *   `Alpine.js` (可选): 轻量级交互逻辑
*   **CI/CD**: GitHub Actions
