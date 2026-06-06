import os
from google import genai
import requests
import json

# 1. 初始化
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# 2. 獲取大盤數據函式
def get_market_data():
    # 優先嘗試抓取即時數據
    live_url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_0000.tw"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(live_url, headers=headers)
        data = res.json()
        
        # 檢查是否有即時成交價 (z)，且不為 "-"
        if 'msgArray' in data and len(data['msgArray']) > 0 and data['msgArray'][0].get('z') != "-":
            return f"盤中即時指數: {data['msgArray'][0]['z']}"
    except:
        pass

    # 若抓不到即時數據，切換抓取收盤指數
    close_url = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_INDEX?response=json"
    try:
        res = requests.get(close_url, headers=headers)
        data = res.json()
        close_value = data['data'][-1][1]
        return f"最近收盤指數: {close_value}"
    except:
        return "暫時無法取得大盤數據"

# 3. 呼叫函式取得數據
market_info = get_market_data()

# 4. 專業經理人 Prompt
prompt = f"""
你現在是一位擁有 20 年經驗的台股專業投資經理人，而我手上有一筆500萬信貸資金，利率2.4%，七年期，預計分批買入大盤，目標標的包含00403A, 0050, 009816, 00981A。請根據以下大盤數據進行深度分析：
數據資料：{market_info}

請依序完成以下任務：
1. 【數據結構化分析】：針對目前或是台股收盤大盤的指數位置、當日波動區間（高低點）進行客觀的價量解讀。
2. 【市場情緒與邏輯推演】：評估目前市場是處於多頭強勢、震盪整理還是空頭趨勢。
3. 【反覆驗證】：請自我檢查上述分析是否與數據矛盾，確保邏輯一致，若指數位置接近關鍵技術點位，請明確指出。
4. 【專業經理人操作建議】：請給出具體的當下或是隔日「觀望/加碼/避險」建議，並說明理由。

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