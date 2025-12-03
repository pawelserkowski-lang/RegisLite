from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from rtc.signaling import router as rtc_router
from debugger.debugger_loop import start_debug_loop
import zipfile
import shutil
import os

app = FastAPI()

# Podpinamy dodatkowy router (na razie prosty placeholder)
app.include_router(rtc_router)


@app.get("/", response_class=HTMLResponse)
def home():
    """Zwraca prosty panel HTML."""
    with open("static/index.html", "r", encoding="utf8") as f:
        return f.read()


@app.post("/upload_zip")
async def upload_zip(f: UploadFile = File(...)):
    """Upload ZIP z projektem i rozpakowanie do workspace/project."""
    os.makedirs("workspace", exist_ok=True)
    zip_path = os.path.join("workspace", "incoming.zip")

    # Zapis pliku
    with open(zip_path, "wb") as w:
        w.write(await f.read())

    project_dir = os.path.join("workspace", "project")
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    os.makedirs(project_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(project_dir)

    return {"status": "uploaded_and_extracted", "project_dir": project_dir}


@app.get("/start_debug")
async def start_debug():
    """Start pętli debuggera."""
    logs = await start_debug_loop()
    return {"logs": logs}
