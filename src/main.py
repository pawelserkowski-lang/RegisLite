import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Importy z wnętrza pakietu
from src.config.env_config import get_config
from src.debugger.debugger_loop import start_debug_loop
from src.rtc.signaling import handle_command
import shutil
import uuid
from fastapi import File, UploadFile, HTTPException, WebSocket

# Inicjalizacja Configu
config = get_config()

app = FastAPI(
    title="RegisLite AI",
    version="5.0.0 (Sentient Edition)",
    description="System autonomicznej naprawy kodu z interfejsem WebSocket"
)

# CORS - Ważne dla developmentu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obsługa statyków
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_root():
    dashboard_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {"message": "RegisLite API is running. Dashboard not found in /static."}

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "mode": "async",
        "model": config.OPENAI_MODEL,
        "workspace_ready": os.path.exists(config.WORKSPACE_DIR)
    }

# --- ENDPOINTY (Przeniesione z dawnego app.py i dostosowane) ---

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(400, detail="Tylko pliki .zip!")
    
    # Generuj ID sesji
    session_id = str(uuid.uuid4())[:8]
    workspace = config.WORKSPACE_DIR / session_id
    project_dir = workspace / "project"
    
    try:
        os.makedirs(project_dir, exist_ok=True)
        zip_path = workspace / "upload.zip"
        
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)
            
        shutil.unpack_archive(zip_path, project_dir)
        return {"session_id": session_id, "message": "Projekt załadowany. Gotowy do debugowania."}
        
    except Exception as e:
        # Sprzątanie po błędzie
        if os.path.exists(workspace):
            shutil.rmtree(workspace)
        raise HTTPException(500, detail=f"Upload failed: {str(e)}")

@app.post("/debug/{session_id}")
async def debug_endpoint(session_id: str):
    # Asynchroniczne uruchomienie pętli debuggera
    try:
        result = await start_debug_loop(session_id)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # handle_command jest generatorem asynchronicznym (yield)
            async for msg in handle_command(data, session_id):
                await websocket.send_text(msg)
    except Exception as e:
        print(f"WS Disconnected: {e}")