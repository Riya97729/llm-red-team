import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

data = {
   "model": "openai/gpt-oss-20b",
    "messages": [
        {"role": "user", "content": "Say hello in one short sentence."}
    ],
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json()["choices"][0]["message"]["content"])