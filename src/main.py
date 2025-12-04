# UWAGA: Ten plik to dawne app.py po refaktoryzacji importów.
# Zakładam typową strukturę FastAPI/Starlette na podstawie nazw plików.

import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# -- ZMIANA IMPORTÓW NA RELATYWNE LUB Z PAKIETU SRC --
# Wcześniej było: from config.env_config import ...
# Teraz, będąc wewnątrz pakietu src, używamy importów absolutnych od roota lub relatywnych.
try:
    from src.config.env_config import Config
    from src.ai.chatgpt_client import ChatGPTClient
    from src.rtc.signaling import signaling_router  # Przykład routera
    from src.debugger.debugger_analyzer import Debugger
except ImportError:
    # Fallback dla IDE, które nie ogarniają path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.env_config import Config
    # ... itd

app = FastAPI(title="RegisLite", version="2.0.0 Modular")

# --- KONFIGURACJA ---
# Obsługa plików statycznych
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- ROUTING ---
# Jeśli masz routery w podmodułach, tutaj je podłączasz
# app.include_router(signaling_router, prefix="/rtc")

@app.get("/")
async def read_root():
    # Serwowanie dashboardu
    dashboard_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "RegisLite API is running. Dashboard not found."}

@app.get("/health")
async def health_check():
    return {"status": "ok", "module": "modular_structure"}

# Tutaj byłaby reszta Twojej logiki z oryginalnego app.py
# Pamiętaj, żeby przenieść logikę biznesową do service'ów w src/services/