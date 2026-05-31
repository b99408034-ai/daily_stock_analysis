import os
from google import genai
import twstock
import requests

# 從環境變數讀取 (GitHub Secrets)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# 2. 獲取並處理資料
stock = twstock.Stock('2330')
data = f"台積電近五日收盤: {stock.price[-5:]}"

# 3. AI 生成報告
response = client.models.generate_content(
    model='gemini-3.1-flash-lite',
    contents=f"請分析以下台股目前大盤數據並給出專業建議: {data}"
)

# 4. 發送至 Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, json={"chat_id": CHAT_ID, "text": response.text})

print("報告已發送至 Telegram！")