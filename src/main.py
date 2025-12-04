import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Importy z wnętrza pakietu
from src.config.env_config import get_config
from src.rtc.signaling import handle_command

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
    """Root endpoint to serve dashboard or info."""
    dashboard_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return {
        "message": "RegisLite API is running. Dashboard not found in /static."
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "operational",
        "mode": "async",
        "model": config.OPENAI_MODEL,
        "workspace_ready": os.path.exists(config.WORKSPACE_DIR)
    }


@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    """Upload a zip file to start a session."""
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
        return {
            "session_id": session_id,
            "message": "Projekt załadowany. Gotowy do debugowania."
        }

    except Exception as e:
        # Sprzątanie po błędzie
        if os.path.exists(workspace):
            shutil.rmtree(workspace)
        raise HTTPException(500, detail=f"Upload failed: {str(e)}")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time interaction."""
    await websocket.accept()
    session_id = client_id  # Assuming client_id acts as session_id for now
    try:
        while True:
            data = await websocket.receive_text()
            # handle_command jest generatorem asynchronicznym (yield)
            async for msg in handle_command(data, session_id):
                await websocket.send_text(msg)
    except Exception as e:
        print(f"WS Disconnected: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
