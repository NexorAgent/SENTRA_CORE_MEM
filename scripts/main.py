from openai import OpenAI

openai_client = OpenAI()
import json
import os

import openai

with open("configs/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = "Bonjour, qui es-tu ?"
response = openai_client.chat.completions.create(
    model=cfg["model"],
    messages=[{"role": "user", "content": prompt}],
    temperature=cfg.get("temperature", 0.5),
    max_tokens=cfg.get("max_tokens", 2048),
)

print(response.choices[0].message["content"])
