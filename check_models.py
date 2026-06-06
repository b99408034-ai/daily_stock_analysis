import os
from google import genai

print("開始檢查模型...") # 強制印出，確認程式有啟動

try:
    # 初始化
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # 獲取模型列表
    models = list(client.models.list())
    print(f"成功獲取到 {len(models)} 個模型")
    
    for model in models:
        print(f"模型名稱: {model.name}")
except Exception as e:
    print(f"發生錯誤: {e}")

print("檢查結束。") # 強制印出，確認程式有跑完