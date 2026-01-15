import akshare as ak
import pandas as pd
import json
import os
from datetime import datetime

OUTPUT_FILE = "data/ai_report.json"

def get_top_gainers_a_share():
    """获取沪深 A 股涨幅前 5"""
    try:
        print("Fetching A-Share spot data...")
        # 东方财富 A股 实时行情
        df = ak.stock_zh_a_spot_em()
        # 按涨跌幅排序
        df.sort_values(by="涨跌幅", ascending=False, inplace=True)
        top5 = df.head(5)
        
        result = []
        for _, row in top5.iterrows():
            result.append(f"{row['名称']} ({row['代码']}): +{row['涨跌幅']}%")
        return result
    except Exception as e:
        print(f"Error fetching A-Share: {e}")
        return []

def get_hk_gainers():
    """获取港股涨幅前 3 (主板)"""
    try:
        print("Fetching HK spot data...")
        df = ak.stock_hk_market_watch(symbol="主板") # 港股主板
        # 注意：Akshare不同接口列名可能不同，需防御性编程
        # 这里假设有一列是涨跌幅
        if '涨跌幅' in df.columns:
            df.sort_values(by="涨跌幅", ascending=False, inplace=True)
            top3 = df.head(3)
            result = []
            for _, row in top3.iterrows():
                result.append(f"{row['名称']} ({row['代码']}): +{row['涨跌幅']}%")
            return result
    except Exception as e:
        print(f"Error fetching HK Stocks: {e}")
        return []

def generate_quant_report():
    print("Generating Daily Quant Report...")
    
    # 1. A股 龙虎榜/涨幅榜
    a_gainers = get_top_gainers_a_share()
    
    # 2. 简易市场情绪判断
    # 这里为了演示，我们直接写死或简单判断。
    # 实际可以根据 fetch_data.py 生成的 market_data.json 来判断指数涨跌。
    
    content = "### 📊 每日量化精选 (规则驱动)\n\n"
    
    content += "#### 🇨🇳 A股今日领涨 (Top 5)\n"
    if a_gainers:
        for item in a_gainers:
            content += f"- {item}\n"
    else:
        content += "- 数据获取暂时不可用\n"
        
    content += "\n#### 💡 投资风向标\n"
    content += "基于动量策略，今日市场热点主要集中在上述领涨板块。建议关注成交量配合放大的个股。\n\n"
    
    # --- DCA 定投回测 (基于已有数据) ---
    try:
        with open("data/market_data.json", 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        content += "#### 💰 定投回测 (近30日模拟)\n"
        content += "| 资产 | 累计投入 | 现值 | 收益率 |\n"
        content += "|---|---|---|---|\n"
        
        for ticker, data in market_data.items():
            # 只计算几个核心资产
            if "Bitcoin" not in data['name'] and "S&P" not in data['name'] and "Gold" not in data['name']:
                continue
                
            history = data.get('history', [])
            if not history: continue
            
            total_invested = 0
            total_shares = 0
            daily_invest = 100 # 每天定投 100 元
            
            for day in history:
                price = day['close']
                if price > 0:
                    shares = daily_invest / price
                    total_shares += shares
                    total_invested += daily_invest
            
            current_price = data['current_price']
            current_value = total_shares * current_price
            return_rate = ((current_value - total_invested) / total_invested) * 100
            
            content += f"| {data['name']} | ${total_invested} | ${round(current_value, 0)} | **{round(return_rate, 2)}%** |\n"
            
        content += "\n*(注：假设每日定投 $100，不含手续费)*\n\n"
        
    except Exception as e:
        print(f"DCA Calc Error: {e}")

    content += "*(注：本报告由 Python 脚本自动生成，非 AI 建议，仅供参考)*"
    
    report = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "content": content,
        "source": "Akshare Quant Rules"
    }
    
    return report

def save_report(report):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Quant Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    report = generate_quant_report()
    save_report(report)
