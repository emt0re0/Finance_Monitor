import akshare as ak
import pandas as pd
import json
import os
import time
from datetime import datetime

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "market_data.json")

# 核心资产列表 (名称汉化)
ASSETS = [
    { "name": "标普500 (SPX)", "type": "us_index", "symbol": ".INX", "ticker_id": "^GSPC" },
    { "name": "纳斯达克 (IXIC)", "type": "us_index", "symbol": ".IXIC", "ticker_id": "^IXIC" },
    { "name": "上证指数 (000001)", "type": "cn_index", "symbol": "sh000001", "ticker_id": "000001.SS" },
    { "name": "沪深300 (000300)", "type": "cn_index", "symbol": "sh000300", "ticker_id": "000300.SS" },
    { "name": "恒生指数 (HSI)", "type": "hk_index", "symbol": "HSI", "ticker_id": "^HSI" },
    { "name": "黄金 (COMEX)", "type": "futures", "symbol": "GC", "ticker_id": "GC=F" },
    { "name": "比特币 (BTC)", "type": "futures", "symbol": "BTC", "ticker_id": "BTC-USD" }, 
]

def load_existing_data():
    """读取已有的 JSON 数据，用于增量更新"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load existing data: {e}")
            return {}
    return {}

def fetch_market_data():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting INCREMENTAL data fetch...")
    
    # 1. 加载旧数据
    existing_data = load_existing_data()
    summary_data = {}

    for asset in ASSETS:
        name = asset['name']
        ticker_id = asset['ticker_id']
        print(f"Fetching {name}...")
        
        try:
            df = None
            
            # 根据类型调用 Akshare 接口
            if asset['type'] == 'cn_index':
                df = ak.stock_zh_index_daily(symbol=asset['symbol'])
            elif asset['type'] == 'us_index':
                df = ak.index_us_stock_sina(symbol=asset['symbol'])
            elif asset['type'] == 'hk_index':
                df = ak.stock_hk_index_daily_sina(symbol=asset['symbol'])
            elif asset['type'] == 'futures':
                df = ak.futures_foreign_hist(symbol=asset['symbol']) 

            if df is None or df.empty:
                print(f"⚠️ No new data for {name}")
                # 如果没有新数据，保留旧数据（如果存在）
                if ticker_id in existing_data:
                    summary_data[ticker_id] = existing_data[ticker_id]
                continue

            # --- 数据清洗与合并逻辑 ---
            
            # 1. 统一列名并设置 Date 索引
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            # 2. 获取现价和涨跌幅 (基于最新抓取的数据)
            df.sort_index(inplace=True)
            current_price = float(df['close'].iloc[-1])
            prev_price = float(df['close'].iloc[-2])
            change_percent = ((current_price - prev_price) / prev_price) * 100
            
            # 3. 构建新的历史列表 (History List)
            new_history = []
            for date, row in df.iterrows():
                new_history.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "close": round(float(row['close']), 2)
                })

            # 4. 智能合并 (Merge Logic)
            # 如果本地已有数据，我们将尝试“最长保留原则”。
            # 但由于 Akshare 每次抓取其实都是抓取全量（或很长一段），
            # 直接使用新抓取的 df 转换为 list 实际上比 "手动 append" 更稳健，
            # 它可以自动修正过去可能修正的数据，并自动包含最新一天。
            # 只要 fetch 的范围足够长 (Akshare通常返回所有历史)，直接覆盖 history 即可。
            # 如果 Akshare 返回的数据变短了 (API限制)，我们需要做 merge。
            
            final_history = new_history
            
            # 简单的检查：如果新数据太少（比如API抽风只返了30天），而旧数据有1000天，那我们只把新数据的最后一天 append 进去
            if ticker_id in existing_data:
                old_history = existing_data[ticker_id].get('history', [])
                if len(old_history) > len(new_history) + 10: 
                    # 只有当新数据显著少于旧数据时，才执行“追加模式”
                    print(f"ℹ️ API returned less data ({len(new_history)}) than local ({len(old_history)}). Using Append Mode.")
                    # 找到旧数据最后一天
                    last_old_date = old_history[-1]['date']
                    # 从新数据中找到该日期之后的所有数据
                    items_to_add = [item for item in new_history if item['date'] > last_old_date]
                    final_history = old_history + items_to_add
            
            # 5. 更新 Summary 对象
            summary_data[ticker_id] = {
                "name": name,
                "current_price": round(current_price, 2),
                "change_percent": round(change_percent, 2),
                "history": final_history,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "currency": "USD" if "USD" in ticker_id or "GSPC" in ticker_id or "IXIC" in ticker_id or "GC" in ticker_id else ("HKD" if "HSI" in ticker_id else "CNY"),
                "source": "Akshare"
            }
            print(f"✅ Updated {name}: Price {round(current_price, 2)}, History Length: {len(final_history)}")
            
        except Exception as e:
            print(f"❌ Error updating {name}: {e}")
            # 出错时保留旧数据
            if ticker_id in existing_data:
                summary_data[ticker_id] = existing_data[ticker_id]
            
    return summary_data

def save_to_json(data):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(data)} assets to {OUTPUT_FILE}")

if __name__ == "__main__":
    data = fetch_market_data()
    save_to_json(data)