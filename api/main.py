from fastapi import FastAPI, Request
from pydantic import BaseModel
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

import json

app = FastAPI()

# Répertoire de stockage mémoire
MEMORY_PATH = "memory"
LOGS_PATH = "logs"

os.makedirs(MEMORY_PATH, exist_ok=True)
os.makedirs(LOGS_PATH, exist_ok=True)

class MemoryBlock(BaseModel):
    project: str
    content: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/status")
def status():
    return {
        "project": "SENTRA_CORE_MEM",
        "version": "v0.2",
        "status": "API opérationnelle"
    }

@app.post("/append")
def append_memory(block: MemoryBlock):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{block.project}_{timestamp}.md"
    filepath = os.path.join(MEMORY_PATH, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(block.content)

    log_entry = {
        "action": "append_memory",
        "file": filename,
        "project": block.project,
        "timestamp": timestamp
    }

    with open(os.path.join(LOGS_PATH, f"log_{timestamp}.json"), "w", encoding="utf-8") as logf:
        json.dump(log_entry, logf, indent=2)

    return {"message": "Mémoire ajoutée", "file": filename}

@app.get("/logs")
def get_logs():
    files = os.listdir(LOGS_PATH)
    logs = []
    for f in files:
        if f.endswith(".json"):
            with open(os.path.join(LOGS_PATH, f), "r", encoding="utf-8") as lf:
                logs.append(json.load(lf))
    return logs
