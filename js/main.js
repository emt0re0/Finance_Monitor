document.addEventListener('DOMContentLoaded', () => {
    const DATA_URL = 'data/market_data.json';
    let marketData = {};
    let chartInstance = null;
    let currentTicker = null;

    // DOM Elements
    const els = {
        cardsContainer: document.getElementById('market-cards'),
        chartSelect: document.getElementById('chart-select'),
        statusBadge: document.getElementById('status-badge'),
        lastUpdated: document.getElementById('last-updated'),
        aiContent: document.getElementById('ai-content'),
        trendChart: document.getElementById('trend-chart'),
        dca: {
            amount: document.getElementById('dca-amount'),
            freq: document.getElementById('dca-freq'),
            start: document.getElementById('dca-start'),
            end: document.getElementById('dca-end'),
            tableBody: document.getElementById('dca-table-body')
        }
    };

    // Init
    fetchData();

    // Event Listeners for DCA
    [els.dca.amount, els.dca.freq, els.dca.start, els.dca.end].forEach(input => {
        input.addEventListener('change', calculateDCA);
    });

    els.chartSelect.addEventListener('change', (e) => {
        updateChart(e.target.value);
    });

    function fetchData() {
        fetch(DATA_URL)
            .then(res => {
                if (!res.ok) throw new Error("Data load failed");
                return res.json();
            })
            .then(data => {
                marketData = data;
                initDashboard();
            })
            .catch(err => {
                console.error(err);
                els.statusBadge.innerText = "OFFLINE";
                els.statusBadge.className = "px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase bg-red-900/20 text-red-500 border border-red-900";
            });
    }

    function initDashboard() {
        const tickers = Object.keys(marketData);
        if (tickers.length === 0) return;

        // 1. Update Status
        const firstItem = marketData[tickers[0]];
        els.statusBadge.innerText = "LIVE";
        els.statusBadge.className = "px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase bg-green-500/20 text-green-400 border border-green-900 shadow-[0_0_10px_rgba(34,197,94,0.3)]";
        els.lastUpdated.innerText = `LAST SYNC: ${firstItem.last_updated || '-'}`;

        // 2. Render Cards
        renderCards(tickers);

        // 3. Init Chart Controls
        renderChartSelect(tickers);
        initChart(tickers[0]);

        // 4. Init DCA Dates (Default: Last 1 Year)
        // Set End Date to Today
        const today = new Date();
        els.dca.end.valueAsDate = today;
        
        // Set Start Date to 1 Year Ago
        const lastYear = new Date();
        lastYear.setFullYear(today.getFullYear() - 1);
        els.dca.start.valueAsDate = lastYear;

        // 5. Run Initial DCA Calculation
        calculateDCA();

        // 6. Load AI Report
        fetchAIReport();
    }

    function renderCards(tickers) {
        els.cardsContainer.innerHTML = '';
        
        tickers.forEach(ticker => {
            const item = marketData[ticker];
            const isUp = item.change_percent >= 0;
            // Chinese Color Style: Red is Up, Green is Down
            const colorClass = isUp ? 'text-red-500' : 'text-green-500'; 
            const bgClass = isUp ? 'bg-red-500/5' : 'bg-green-500/5';
            const borderClass = isUp ? 'border-red-500/20' : 'border-green-500/20';
            
            const arrow = isUp ? '▲' : '▼';
            const sign = isUp ? '+' : '';

            // Detect Currency
            let currency = '$';
            if (item.currency === 'CNY') currency = '¥';
            if (item.currency === 'HKD') currency = 'HK$';

            const card = document.createElement('div');
            card.className = `card cursor-pointer group hover:border-gray-600 relative overflow-hidden`;
            card.onclick = () => {
                els.chartSelect.value = ticker;
                updateChart(ticker);
            };

            card.innerHTML = `
                <div class="absolute top-0 right-0 p-2 opacity-10 text-4xl font-bold font-mono z-0">${ticker.split('.')[0]}</div>
                <div class="relative z-10">
                    <div class="flex justify-between items-start mb-3">
                        <h3 class="text-gray-300 font-bold text-sm tracking-wide group-hover:text-white transition-colors">${item.name}</h3>
                    </div>
                    <div class="flex items-baseline gap-2 mb-2">
                        <span class="text-2xl font-bold text-white tracking-tight font-mono">${currency}${item.current_price.toLocaleString()}</span>
                    </div>
                    <div class="text-xs font-bold ${colorClass} ${bgClass} ${borderClass} border inline-flex items-center px-2 py-1 rounded">
                        <span class="mr-1 text-[10px]">${arrow}</span>
                        <span>${sign}${item.change_percent}%</span>
                    </div>
                </div>
            `;
            els.cardsContainer.appendChild(card);
        });
    }

    function renderChartSelect(tickers) {
        els.chartSelect.innerHTML = '';
        tickers.forEach(ticker => {
            const opt = document.createElement('option');
            opt.value = ticker;
            opt.innerText = marketData[ticker].name;
            els.chartSelect.appendChild(opt);
        });
    }

    function initChart(ticker) {
        chartInstance = echarts.init(els.trendChart);
        updateChart(ticker);
        window.addEventListener('resize', () => chartInstance.resize());
    }

    function updateChart(ticker) {
        if (!marketData[ticker]) return;
        currentTicker = ticker;
        els.chartSelect.value = ticker; 

        const item = marketData[ticker];
        const dates = item.history.map(h => h.date);
        const prices = item.history.map(h => h.close);

        const isUp = item.change_percent >= 0;
        // Chart Colors
        const lineColor = isUp ? '#f87171' : '#4ade80'; // Tailwind red-400 : green-400
        const areaStart = isUp ? 'rgba(248, 113, 113, 0.25)' : 'rgba(74, 222, 128, 0.25)';

        // Calculate default zoom range (Last 1 Year)
        let startPct = 0;
        if (dates.length > 0) {
            const oneYearAgo = new Date();
            oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
            const oneYearAgoStr = oneYearAgo.toISOString().split('T')[0];
            
            const index = dates.findIndex(d => d >= oneYearAgoStr);
            if (index !== -1) {
                startPct = (index / dates.length) * 100;
            } else {
                startPct = 0; // If data is less than a year, show all
            }
        }

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                borderColor: '#334155',
                padding: [10, 15],
                textStyle: { color: '#e2e8f0', fontFamily: 'JetBrains Mono' },
                formatter: (params) => {
                    const p = params[0];
                    return `<div class="font-bold text-xs text-gray-400 mb-1">${p.axisValue}</div>
                            <div class="text-sm">
                                <span style="color:${lineColor}">●</span> ${item.name}: <b class="text-white">${p.data}</b>
                            </div>`;
                }
            },
            grid: { top: 20, right: 20, bottom: 40, left: 50, containLabel: true },
            dataZoom: [
                {
                    type: 'inside', // Enable Mouse Wheel Zoom
                    start: startPct, 
                    end: 100
                },
                {
                    type: 'slider', // Bottom Slider
                    borderColor: '#374151',
                    textStyle: { color: '#9ca3af' },
                    handleStyle: { color: '#3b82f6' },
                    dataBackground: {
                        lineStyle: { color: '#475569' },
                        areaStyle: { color: '#1e293b' }
                    },
                    selectedDataBackground: {
                        lineStyle: { color: '#60a5fa' },
                        areaStyle: { color: '#3b82f6', opacity: 0.2 }
                    },
                    start: startPct,
                    end: 100
                }
            ],
            xAxis: {
                type: 'category',
                data: dates,
                axisLine: { lineStyle: { color: '#334155' } },
                axisLabel: { color: '#64748b', fontSize: 10, fontFamily: 'JetBrains Mono' },
                axisTick: { show: false }
            },
            yAxis: {
                type: 'value',
                scale: true,
                splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
                axisLabel: { color: '#64748b', fontSize: 10, fontFamily: 'JetBrains Mono' }
            },
            series: [{
                name: item.name,
                type: 'line',
                data: prices,
                smooth: true,
                showSymbol: false,
                lineStyle: { color: lineColor, width: 2 },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: areaStart },
                        { offset: 1, color: 'rgba(0,0,0,0)' }
                    ])
                }
            }]
        };
        chartInstance.setOption(option);
    }

    function calculateDCA() {
        const amount = parseFloat(els.dca.amount.value) || 0;
        const freq = els.dca.freq.value; 
        const startDate = new Date(els.dca.start.value);
        const endDate = new Date(els.dca.end.value);

        // Validation
        if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return;

        els.dca.tableBody.innerHTML = '';

        Object.keys(marketData).forEach(ticker => {
            const item = marketData[ticker];
            const history = item.history;
            if (!history || history.length < 2) return;

            // Filter
            const periodData = history.filter(h => {
                const d = new Date(h.date);
                return d >= startDate && d <= endDate;
            });

            if (periodData.length === 0) return;

            let totalInvested = 0;
            let totalShares = 0;
            let lastInvestDate = null;

            periodData.forEach(day => {
                const date = new Date(day.date);
                let shouldInvest = false;

                if (freq === 'daily') {
                    shouldInvest = true;
                } else if (freq === 'weekly') {
                    const currentWeek = getWeekNumber(date);
                    const lastWeek = lastInvestDate ? getWeekNumber(lastInvestDate) : -1;
                    if (currentWeek !== lastWeek) shouldInvest = true; 
                } else if (freq === 'monthly') {
                     const currentMonth = date.getMonth();
                     const lastMonth = lastInvestDate ? lastInvestDate.getMonth() : -1;
                     if (currentMonth !== lastMonth) shouldInvest = true;
                }

                if (shouldInvest && day.close > 0) {
                    totalShares += amount / day.close;
                    totalInvested += amount;
                    lastInvestDate = date;
                }
            });

            const finalPrice = periodData[periodData.length - 1].close;
            const finalValue = totalShares * finalPrice;
            const profit = finalValue - totalInvested;
            const returnRate = totalInvested > 0 ? (profit / totalInvested) * 100 : 0;

            const isProfitable = profit >= 0;
            const colorClass = isProfitable ? 'text-red-400' : 'text-green-400';
            const sign = isProfitable ? '+' : '';

            const row = document.createElement('tr');
            row.className = "hover:bg-gray-800/50 transition-colors border-b border-gray-800 last:border-0";
            row.innerHTML = `
                <td class="px-4 py-3 font-medium text-gray-300 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full ${isProfitable ? 'bg-red-500' : 'bg-green-500'}"></span>
                    ${item.name.split('(')[0]}
                </td>
                <td class="px-4 py-3 text-gray-500 font-mono text-xs">$${totalInvested.toLocaleString()}</td>
                <td class="px-4 py-3 text-white font-mono text-xs font-bold">$${finalValue.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                <td class="px-4 py-3 text-right font-mono text-xs font-bold ${colorClass}">${sign}${returnRate.toFixed(2)}%</td>
            `;
            els.dca.tableBody.appendChild(row);
        });
    }
    
    function getWeekNumber(d) {
        d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
        d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
        var yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
        var weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7);
        return weekNo;
    }

    function fetchAIReport() {
        fetch('data/ai_report.json')
            .then(res => {
                if(!res.ok) throw new Error();
                return res.json();
            })
            .then(report => {
                const contentHtml = marked.parse(report.content);
                els.aiContent.innerHTML = `
                    <div class="prose prose-invert prose-sm max-w-none text-gray-300">
                        ${contentHtml}
                    </div>
                    <div class="text-[10px] text-gray-600 mt-6 pt-2 border-t border-gray-800 flex justify-between font-mono">
                        <span>SOURCE: ${report.source}</span>
                        <span>GENERATED: ${report.date}</span>
                    </div>
                `;
            })
            .catch(() => {
                els.aiContent.innerHTML = `<div class="text-center py-10 text-gray-600 font-mono text-xs">Waiting for data stream...</div>`;
            });
    }
});