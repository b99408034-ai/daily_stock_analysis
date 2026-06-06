import os
import requests
import json
import feedparser
import yfinance as yf
from google import genai

# 1. 初始化
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# 2. 數據抓取函式區
def get_market_data():
    """抓取台股大盤指數"""
    live_url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_0000.tw"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(live_url, headers=headers)
        data = res.json()
        if 'msgArray' in data and len(data['msgArray']) > 0 and data['msgArray'][0].get('z') != "-":
            return f"盤中即時指數: {data['msgArray'][0]['z']}"
    except: pass
    
    close_url = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_INDEX?response=json"
    try:
        res = requests.get(close_url, headers=headers)
        data = res.json()
        return f"最近收盤指數: {data['data'][-1][1]}"
    except:
        return "暫時無法取得台股指數"

def get_us_market_data():
    """抓取美股指標 (^GSPC: S&P500, ^IXIC: Nasdaq)"""
    try:
        tickers = yf.Tickers("^GSPC ^IXIC")
        results = ""
        for symbol in tickers.tickers:
            price = tickers.tickers[symbol].info.get('regularMarketPrice')
            results += f"{symbol} 指數: {price}, "
        return results
    except:
        return "暫時無法取得美股數據"

def get_financial_news():
    """抓取鉅亨網財經新聞 (RSS)"""
    rss_url = "https://news.cnyes.com/rss/news/headline"
    feed = feedparser.parse(rss_url)
    news_summary = ""
    for entry in feed.entries[:3]:
        news_summary += f"- {entry.title}\n"
    return news_summary

# 3. 執行資料聚合
market_info = get_market_data()
us_info = get_us_market_data()
news_info = get_financial_news()

# 4. AI 專業分析 Prompt
prompt = f"""
你現在是一位擁有 20 年經驗的台股專業投資經理人。
手上有 500 萬台幣信貸資金(利率2.4%，七年期)，目標標的包含 00403A, 0050, 009816, 00981A。

請根據以下最新數據進行深度關聯分析：
【台股數據】：{market_info}
【美股數據】：{us_info}
【今日財經頭條】：
{news_info}

請執行以下綜合判斷：
1. 【跨市場關聯】：美股昨夜的走勢如何影響今日台股的開盤情緒？
2. 【數據結構化分析】：針對目前或是台股收盤大盤的指數位置、當日波動區間（高低點）進行客觀的價量解讀。
3. 【市場情緒與邏輯推演】：評估目前市場是處於多頭強勢、震盪整理還是空頭趨勢。
4. 【反覆驗證】：請自我檢查上述分析是否與數據矛盾，確保邏輯一致，若指數位置接近關鍵技術點位，請明確指出。
5. 【專業經理人操作建議】：請給出具體的當下或是隔日「觀望/加碼/避險」建議，並說明理由。

要求：語氣需專業、客觀，請以「建議策略」作為結尾。
"""

# 5. AI 生成報告並發送
try:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    
    payload = {"chat_id": CHAT_ID, "text": response.text}
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, json=payload)
    
    if res.status_code == 200:
        print("報告成功發送至 Telegram！")
    else:
        print(f"發送失敗！狀態碼: {res.status_code}")
        print(f"Telegram 回應內容: {res.text}")

except Exception as e:
    print(f"程式執行異常: {e}")