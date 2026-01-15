import akshare as ak
import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "market_data.json")

def fetch_market_data():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting REAL data fetch via Akshare...")
    
    summary_data = {}

    # 定义资产配置
    ASSETS = [
        { "name": "S&P 500", "type": "us_index", "symbol": ".INX", "ticker_id": "^GSPC" },
        { "name": "Nasdaq", "type": "us_index", "symbol": ".IXIC", "ticker_id": "^IXIC" },
        { "name": "SSE Composite", "type": "cn_index", "symbol": "sh000001", "ticker_id": "000001.SS" },
        { "name": "CSI 300", "type": "cn_index", "symbol": "sh000300", "ticker_id": "000300.SS" },
        { "name": "Hang Seng", "type": "hk_index", "symbol": "HSI", "ticker_id": "^HSI" },
        # 外盘期货 (新浪源)
        { "name": "Gold (COMEX)", "type": "futures", "symbol": "GC", "ticker_id": "GC=F" },
        { "name": "Bitcoin (CME Futures)", "type": "futures", "symbol": "BTC", "ticker_id": "BTC-USD" }, 
    ]

    for asset in ASSETS:
        name = asset['name']
        print(f"Fetching {name}...")
        
        try:
            df = None
            
            if asset['type'] == 'cn_index':
                df = ak.stock_zh_index_daily(symbol=asset['symbol'])
                
            elif asset['type'] == 'us_index':
                df = ak.index_us_stock_sina(symbol=asset['symbol'])
            
            elif asset['type'] == 'hk_index':
                df = ak.stock_hk_index_daily_sina(symbol=asset['symbol'])
                
            elif asset['type'] == 'futures':
                # 新浪外盘期货历史行情
                df = ak.futures_foreign_hist(symbol=asset['symbol']) 

            if df is None or df.empty:
                print(f"⚠️ No data for {name}")
                continue

            # 数据清洗：Akshare 返回的列名可能不一致
            # futures_foreign_hist 返回: date, open, high, low, close, volume...
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            df.sort_index(inplace=True)
            
            # 取最近30天
            recent_df = df.iloc[-30:]
            
            current_price = float(recent_df['close'].iloc[-1])
            prev_price = float(recent_df['close'].iloc[-2])
            change_percent = ((current_price - prev_price) / prev_price) * 100
            
            history_list = []
            for date, row in recent_df.iterrows():
                history_list.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "close": round(float(row['close']), 2)
                })
            
            summary_data[asset['ticker_id']] = {
                "name": name,
                "current_price": round(current_price, 2),
                "change_percent": round(change_percent, 2),
                "history": history_list,
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "source": "Akshare (Sina)"
            }
            print(f"✅ Success: {name} at {round(current_price, 2)}")
            
        except Exception as e:
            print(f"❌ Error {name}: {e}")
            
    return summary_data

def save_to_json(data):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} assets to {OUTPUT_FILE}")

if __name__ == "__main__":
    data = fetch_market_data()
    save_to_json(data)
