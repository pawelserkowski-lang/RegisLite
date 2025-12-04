# app.py
import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from debugger.loop import start_debug_loop

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/dashboard.html", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(400, detail="Tylko pliki .zip!")
    
    session_id = str(uuid.uuid4())[:8]
    workspace = f"workspace/{session_id}"
    os.makedirs(f"{workspace}/project", exist_ok=True)
    
    zip_path = f"{workspace}/upload.zip"
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    shutil.unpack_archive(zip_path, f"{workspace}/project")
    return {"session_id": session_id, "message": "ZIP wgrany – kliknij Start Debug!"}

@app.post("/debug/{session_id}")
async def debug(session_id: str):
    try:
        result = await start_debug_loop(session_id)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
