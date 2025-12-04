# app.py
import os
import shutil
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from debugger.loop import start_debug_loop
import uuid

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/dashboard.html", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())[:8]
    workspace = f"workspace/{session_id}"
    os.makedirs(workspace, exist_ok=True)
    
    zip_path = f"{workspace}/upload.zip"
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    shutil.unpack_archive(zip_path, f"{workspace}/project")
    
    return {"session_id": session_id, "message": "ZIP wgrany – kliknij Start Debug!"}

@app.post("/debug/{session_id}")
async def debug(session_id: str):
    result = await start_debug_loop(session_id)
    return result

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"RegisLite mowi: {data}")
    except WebSocketDisconnect:
        pass
