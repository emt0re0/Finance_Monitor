document.addEventListener('DOMContentLoaded', () => {
    const DATA_URL = 'data/market_data.json';
    let marketData = {};
    let chartInstance = null;

    // Fetch Data
    fetch(DATA_URL)
        .then(response => {
            if (!response.ok) throw new Error("Failed to load data");
            return response.json();
        })
        .then(data => {
            marketData = data;
            initDashboard(data);
        })
        .catch(err => {
            console.error(err);
            document.getElementById('status-badge').innerText = "加载错误";
            document.getElementById('status-badge').className = "px-3 py-1 rounded-full text-xs font-semibold bg-red-900 text-red-200";
        });

    function initDashboard(data) {
        // Update Status
        const timestamp = new Date().toLocaleString();
        const badge = document.getElementById('status-badge');
        badge.innerText = `数据已更新`;
        badge.className = "px-3 py-1 rounded-full text-xs font-semibold bg-green-900 text-green-200";

        // Render Cards
        renderCards(data);

        // Init Chart with first asset
        const firstKey = Object.keys(data)[0];
        initChart(firstKey);

        // Fetch AI Report
        fetchAIReport();
    }

    function fetchAIReport() {
        fetch('data/ai_report.json')
            .then(res => {
                if (!res.ok) throw new Error("Report not found");
                return res.json();
            })
            .then(report => {
                const container = document.getElementById('ai-content');
                container.innerHTML = `
                    <div class="prose prose-invert prose-sm max-w-none">
                        ${marked.parse(report.content)}
                    </div>
                    <div class="text-xs text-gray-500 mt-3 flex justify-between">
                        <span>来源: ${report.source}</span>
                        <span>日期: ${report.date}</span>
                    </div>
                `;
            })
            .catch(err => {
                console.log("AI Report missing:", err);
                document.getElementById('ai-content').innerHTML = `
                    <p class="text-gray-400 italic">等待下一次调度更新...</p>
                `;
            });
    }

    function renderCards(data) {
        const container = document.getElementById('market-cards');
        container.innerHTML = '';

        Object.keys(data).forEach(key => {
            const item = data[key];
            const isPositive = item.change_percent >= 0;
            const colorClass = isPositive ? 'text-green-400' : 'text-red-400';
            const arrow = isPositive ? '▲' : '▼';
            
            // 简单的货币猜测逻辑
            let currency = '
});
