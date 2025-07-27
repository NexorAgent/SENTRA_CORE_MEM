
import requests

ZEP_URL = "http://localhost:8002"

def save_to_zep(session_id: str, role: str, content: str):
    url = f"{ZEP_URL}/api/v1/memory/{session_id}"
    return requests.post(url, json={"messages": [{"role": role, "content": content}]})

def search_zep(session_id: str, query: str):
    url = f"{ZEP_URL}/api/v1/memory/search/{session_id}"
    r = requests.get(url, params={"query": query})
    return r.json() if r.ok else {"error": r.text}
