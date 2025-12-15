#from google import genai
#from google.genai import types

#GEMINI_API_KEY = "AIzaSyDCRABzmOMdGrepcllfcYUt3xRiJ0PIFZk"
#client = genai.Client(api_key=GEMINI_API_KEY)

#MODEL_ID = "gemini-2.5-flash" # モデルを選択

#response = client.models.generate_content(
#    model=MODEL_ID,
#    contents="この文章が見えていますか"
#)
#print(response.text)

import os
import google.generativeai as genai

def generate_text(prompt: str, model_id: str | None = None, timeout: int = 60) -> str:
    """
    Google GenAI（Gemini）を呼び出してテキストを生成して返す。
    APIキーは環境変数 `GOOGLE_API_KEY` から取得します。
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY environment variable")

    genai.configure(api_key=api_key)
    model = model_id or "gemini-2.5-flash"

    try:
        response = genai.GenerativeModel(model).generate_content(prompt)
        text = getattr(response, "text", None)
        if text:
            return text
        return str(response)
    except Exception as e:
        # エラーの詳細をログに出力
        print(f"Gemini API Error: {str(e)}")
        raise