import os
from google import genai
import twstock
import requests

# 1. 初始化
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# 2. 獲取大盤數據 (加入防呆)
try:
    index_data = twstock.realtime.get('0000')
    if 'realtime' in index_data:
        current_index = index_data['realtime']['latest_trade_price']
        data = f"大盤指數: {current_index}, 最高: {index_data['realtime']['high']}, 最低: {index_data['realtime']['low']}"
    else:
        # 如果是假日或非交易時段，給予一個備用文字
        data = "目前非交易時段，無法取得最新即時指數。"
except Exception as e:
    data = "數據獲取發生異常，請參考過去盤勢。"

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
try:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt
    )
    payload = {"chat_id": CHAT_ID, "text": response.text}
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    print("報告已發送！")
except Exception as e:
    print(f"發送失敗: {e}")