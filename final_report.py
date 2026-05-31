import os
import requests
from bs4 import BeautifulSoup
from google import genai
import twstock

# 初始化
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 1. 抓取籌碼資料 (三大法人)
majors = twstock.majors()
# 取前五名買超個股作為數據分析參考
top_buys = majors[:5] 
major_data = f"三大法人買超前五: {top_buys}"

# 2. 抓取新聞標題 (以雅虎奇摩股市為例)
def get_stock_news():
    url = "https://tw.stock.yahoo.com/news/category/headline"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_titles = [item.text for item in soup.find_all('h3')[:5]] # 取前五則頭條
    return "\n".join(news_titles)

news_data = get_stock_news()

# 3. 整合所有數據
index_data = twstock.realtime.get('0000')
market_summary = f"大盤指數: {index_data['realtime']['latest_trade_price']}, {major_data}, 最新頭條: {news_data}"

# 4. 進階專業經理人 Prompt
prompt = f"""
你現在是一位擁有 20 年經驗的台股專業投資經理人，而我手上有一筆500萬信貸資金，利率2.4%，七年期，預計分批買入大盤，目標標的包含00403A, 0050, 009816, 00981A。請根據以下大盤數據進行深度分析：
數據資料：{data}

請依序完成以下任務：
1. 【數據結構化分析】：針對目前大盤的指數位置、當日波動區間（高低點）進行客觀的價量解讀。
2. 【市場情緒與邏輯推演】：評估目前市場是處於多頭強勢、震盪整理還是空頭趨勢。
3. 【反覆驗證】：請自我檢查上述分析是否與數據矛盾，確保邏輯一致，若指數位置接近關鍵技術點位，請明確指出。
4. 【專業經理人操作建議】：請給出具體的「觀望/加碼/避險」建議，並說明理由。

要求：語氣需專業、客觀，請以「建議策略」作為結尾。
"""

# 5. AI 生成報告
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=prompt
)

# 6. 發送至 Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": response.text}
res = requests.post(url, json=payload)

print(f"Telegram 回應狀態碼: {res.status_code}")