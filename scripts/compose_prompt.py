from openai import OpenAI
openai_client = OpenAI()
import openai, json, sys, zlib, base64, os

with open("configs/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")  # Clé lue depuis environnement
ctx = sys.argv[1] if len(sys.argv) > 1 else "REZO2410"
with open(f"memories/{ctx}.zmem", "rb") as f:
    z = zlib.decompress(base64.b85decode(f.read())).decode("utf-8")

messages = [{"role": "system", "content": z}, {"role": "user", "content": "Que contient cette mémoire ?"}]
res = openai_client.chat.completions.create(
    model=cfg["model"],
    messages=messages,
    temperature=cfg.get("temperature", 0.5),
    max_tokens=cfg.get("max_tokens", 2048)
)
print(res.choices[0].message["content"])
