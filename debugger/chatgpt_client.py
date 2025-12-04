# debugger/chatgpt_client.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(prompt: str, model: str = "gpt-4o-mini"):
    if not os.getenv("OPENAI_API_KEY"):
        return "[ERROR] Brak klucza OpenAI – używam fake diffa"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT ERROR] {str(e)} → używam fake diffa"
