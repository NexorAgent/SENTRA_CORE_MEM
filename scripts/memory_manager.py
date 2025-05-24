import json, datetime

MEM_PATH = "memory/sentra_memory.json"

def append_memory(contenu, typ="log"):
    with open(MEM_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append({
            "date": datetime.date.today().isoformat(),
            "type": typ,
            "contenu": contenu
        })
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)

def query_memory(limit=5):
    with open(MEM_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data[-limit:]

def search_memory(keyword):
    with open(MEM_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [entry for entry in data if keyword.lower() in entry["contenu"].lower()]
