import json
import os
import google.generativeai as genai
from datetime import datetime

# 配置
INPUT_FILE = "data/market_data.json"
OUTPUT_FILE = "data/ai_report.json"

def load_market_data():
    if not os.path.exists(INPUT_FILE):
        return None
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_report(market_data):
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Generating mock report.")
        return generate_mock_report(market_data)

    print("🤖 Calling Gemini API for analysis...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 构建 Prompt
        # 将 JSON 数据简化为字符串
        data_summary = ""
        for ticker, info in market_data.items():
            data_summary += f"- {info['name']}: Price {info['current_price']} {info.get('currency', 'USD')}, Change {info['change_percent']}%\n"
            
        prompt = f"""
        You are a senior financial analyst. Based on the following daily market data, provide a concise market summary and investment outlook. 
        
        Market Data:
        {data_summary}
        
        Requirements:
        1. Keep it under 150 words.
        2. Highlight the best and worst performers.
        3. Provide a brief sentiment analysis (Bullish/Bearish/Neutral).
        4. Output format: Plain text or simple Markdown (no complex headers).
        """
        
        response = model.generate_content(prompt)
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "content": response.text,
            "source": "Gemini Pro"
        }
        
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return generate_mock_report(market_data)

def generate_mock_report(market_data):
    """当没有 API Key 时生成的占位报告"""
    
    # 简单的逻辑生成
    best_performer = max(market_data.values(), key=lambda x: x['change_percent'])
    worst_performer = min(market_data.values(), key=lambda x: x['change_percent'])
    
    content = (
        f"**Market Summary (Mock Generated)**\n\n"
        f"Today's market shows mixed signals. The top performer is **{best_performer['name']}** "
        f"with a gain of {best_performer['change_percent']}%, showing strong momentum. "
        f"Conversely, **{worst_performer['name']}** lagged behind.\n\n"
        f"Investors should monitor volatility in the coming days. "
        f"(Note: Configure GEMINI_API_KEY in GitHub Secrets to unlock real AI analysis.)"
    )
    
    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "content": content,
        "source": "Local Mock Logic"
    }

def save_report(report):
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    data = load_market_data()
    if data:
        report = generate_report(data)
        save_report(report)
    else:
        print("No market data found to analyze.")
