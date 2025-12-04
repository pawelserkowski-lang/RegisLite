# app.py - FIXED VERSION
import os
import shutil
import uuid
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from debugger.debugger_loop import start_debug_loop
from rtc.signaling import handle_command

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_ZIP_SIZE = 50 * 1024 * 1024  # 50MB

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/dashboard.html", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health():
    """Healthcheck endpoint - sprawdza stan aplikacji"""
    return {
        "status": "ok",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "workspace_exists": os.path.exists("workspace"),
        "version": "4.5-fixed"
    }

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(400, detail="Tylko pliki .zip!")
    
    # Walidacja rozmiaru
    content = await file.read()
    if len(content) > MAX_ZIP_SIZE:
        raise HTTPException(413, detail="ZIP za duży! Maksymalny rozmiar: 50MB")
    
    session_id = str(uuid.uuid4())[:8]
    workspace = f"workspace/{session_id}"
    os.makedirs(f"{workspace}/project", exist_ok=True)
    
    zip_path = f"{workspace}/upload.zip"
    with open(zip_path, "wb") as f:
        f.write(content)
    
    try:
        shutil.unpack_archive(zip_path, f"{workspace}/project")
    except Exception as e:
        raise HTTPException(400, detail=f"Błąd rozpakowywania ZIP: {str(e)}")
    
    return {"session_id": session_id, "message": "ZIP wgrany – kliknij Start Debug!"}

@app.post("/debug/{session_id}")
async def debug(session_id: str):
    workspace = f"workspace/{session_id}"
    if not os.path.exists(workspace):
        raise HTTPException(404, detail="Session nie istnieje!")
    
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
            result = await handle_command(data, session_id)
            await websocket.send_text(result)
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
