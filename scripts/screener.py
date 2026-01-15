import akshare as ak
import pandas as pd
import json
import os
from datetime import datetime

OUTPUT_FILE = "data/ai_report.json"
MARKET_DATA_FILE = "data/market_data.json"

def get_cn_value_movers():
    """A股 价值/蓝筹 异动榜
    标准: 总市值 > 500亿, 0 < 市盈率 < 60
    """
    try:
        print("Fetching A-Share data (Value Filter)...")
        df = ak.stock_zh_a_spot_em()
        df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
        df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
        
        mask = (df['总市值'] > 500_0000_0000) & (df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 60)
        filtered_df = df[mask].copy()
        filtered_df.sort_values(by="涨跌幅", ascending=False, inplace=True)
        
        top = filtered_df.head(5)
        return [f"{row['名称']} ({row['代码']}): +{row['涨跌幅']}% (PE: {row['市盈率-动态']})" for _, row in top.iterrows()]
    except Exception as e:
        print(f"A-Share Error: {e}")
        return []

def get_hk_value_movers():
    """港股 核心资产 异动榜
    标准: 最新价 > 5.0, 成交额 > 1亿 (作为大盘股替代标准)
    """
    try:
        print("Fetching HK data (Liquidity Filter)...")
        df = ak.stock_hk_spot_em()
        df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
        df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        
        # 价格 > 5 且 成交额 > 1亿 HKD (筛选活跃蓝筹)
        mask = (df['最新价'] > 5.0) & (df['成交额'] > 1_0000_0000)
        filtered_df = df[mask].copy()
        filtered_df.sort_values(by="涨跌幅", ascending=False, inplace=True)
        
        top = filtered_df.head(3)
        return [f"{row['名称']} ({row['代码']}): +{row['涨跌幅']}%" for _, row in top.iterrows()]
    except Exception as e:
        print(f"HK Stocks Error: {e}")
        return []

def get_us_value_movers():
    """美股 价值科技 异动榜
    标准: 总市值 > 500亿 USD, 0 < 市盈率 < 60
    """
    try:
        print("Fetching US data (Value Filter)...")
        df = ak.stock_us_famous_spot_em(symbol="科技类") 
        df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
        df['市盈率'] = pd.to_numeric(df['市盈率'], errors='coerce')
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        
        # 市值 > 500亿 USD, PE < 60
        mask = (df['总市值'] > 500_0000_0000) & (df['市盈率'] > 0) & (df['市盈率'] < 60)
        filtered_df = df[mask].copy()
        filtered_df.sort_values(by="涨跌幅", ascending=False, inplace=True)
        
        top = filtered_df.head(3)
        return [f"{row['名称']}: +{row['涨跌幅']}% (PE: {row['市盈率']})" for _, row in top.iterrows()]
    except Exception as e:
        print(f"US Stocks Error: {e}")
        return []

def generate_report():
    print("Generating Global Value Report...")
    
    cn_list = get_cn_value_movers()
    hk_list = get_hk_value_movers()
    us_list = get_us_value_movers()
    
    # 情绪判断
    sentiment = "观察 (Neutral)"
    sentiment_icon = "⚪"
    try:
        if os.path.exists(MARKET_DATA_FILE):
            with open(MARKET_DATA_FILE, 'r', encoding='utf-8') as f:
                m_data = json.load(f)
                spx_chg = m_data.get('^GSPC', {}).get('change_percent', 0)
                sh_chg = m_data.get('000001.SS', {}).get('change_percent', 0)
                if spx_chg > 0 and sh_chg > 0: 
                    sentiment = "乐观 (Bullish) 🟢"
                elif spx_chg < 0 and sh_chg < 0: 
                    sentiment = "谨慎 (Cautious) 🟠"
    except: pass

    content = f"### 💎 全球核心资产动态 (Value Monitor)\n\n"
    content += f"> ⚠️ **免责声明**: 本报告仅供学习与研究参考，不构成任何投资建议。市场有风险，入市需谨慎。\n\n"
    content += f"**今日市场基调**: {sentiment}\n\n"
    
    content += "#### 🇨🇳 A股核心资产 (Large Cap Value)\n"
    content += "*(市值>500亿, 0<PE<60)*\n"
    if cn_list:
        for item in cn_list: content += f"- {item}\n"
    else: content += "- 无符合条件的标的\n"
    
    content += "\n#### 🇭🇰 港股蓝筹动向 (HK Blue Chips)\n"
    content += "*(价格>5.0, 成交额>1亿)*\n"
    if hk_list:
        for item in hk_list: content += f"- {item}\n"
    else: content += "- 无符合条件的标的\n"

    content += "\n#### 🇺🇸 美股价值科技 (US Value Tech)\n"
    content += "*(市值>500亿$, 0<PE<60)*\n"
    if us_list:
        for item in us_list: content += f"- {item}\n"
    else: content += "- 无符合条件的标的\n"
    
    content += "\n---\n"
    content += "#### 🧠 价值投资笔记\n"
    content += "坚持寻找具有护城河、估值合理的卓越企业。每日波动只是噪音，核心在于资产的长期复利能力。结合 AI 分析可以进一步过滤情绪噪音，识别真正的价值洼地。\n"
    
    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "content": content,
        "source": "Global Value Strategy"
    }

if __name__ == "__main__":
    report = generate_report()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("Report Generated Successfully.")
