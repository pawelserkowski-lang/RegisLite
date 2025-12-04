Write-Host "=== RegisLite INTELLIGENCE UPGRADE ===" -ForegroundColor Cyan
Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# ========================================================
# 1. ULEPSZONY KLIENT AI (Z obsługą intencji i statystyk)
# ========================================================
$clientCode = @'
import os
import time
import json
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def _call_gpt(messages, model=None, json_mode=False):
    """Pomocnicza funkcja do wołania API"""
    if not OPENAI_API_KEY:
        raise Exception("Brak klucza API!")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model or OPENAI_MODEL,
        "messages": messages
    }
    
    if json_mode:
        data["response_format"] = {"type": "json_object"}

    start_time = time.time()
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    duration = time.time() - start_time
    
    if resp.status_code != 200:
        raise Exception(f"OpenAI Error {resp.status_code}: {resp.text}")

    content = resp.json()["choices"][0]["message"]["content"]
    return content, duration, (model or OPENAI_MODEL)

async def classify_intent(user_input: str):
    """
    Analizuje co użytkownik miał na myśli.
    Zwraca JSON: { "tool": "sh"|"py"|"ai"|"file", "args": "..." }
    """
    system_prompt = """
    Jesteś routerem komend dla systemu RegisLite.
    Twoim zadaniem jest klasyfikacja intencji użytkownika na jedną z kategorii:
    - "sh": komendy systemowe (git, ls, dir, mkdir, instalacja pakietów)
    - "py": krótki kod python do obliczeń lub testów
    - "file": operacje na plikach (czytanie, zapisywanie)
    - "ai": zwykła rozmowa, pytania o kod, prośby o wyjaśnienie
    
    Zwróć TYLKO JSON w formacie: {"tool": "...", "args": "..."}.
    Przykład: "pokaż pliki" -> {"tool": "sh", "args": "dir"}
    Przykład: "policz 2+2" -> {"tool": "py", "args": "print(2+2)"}
    """
    
    try:
        content, duration, model = _call_gpt(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            model="gpt-4o-mini", # Używamy szybkiego modelu do routingu
            json_mode=True
        )
        return json.loads(content), duration, model
    except Exception as e:
        # Fallback do zwykłego AI
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"

async def ask_with_stats(prompt: str):
    """Zwykłe zapytanie, ale zwraca też metadane"""
    content, duration, model = _call_gpt([{"role": "user", "content": prompt}])
    return content, duration, model

# Kompatybilność wsteczna dla starych modułów
async def ask(prompt: str) -> str:
    c, _, _ = await ask_with_stats(prompt)
    return c
'@
$clientCode | Set-Content "ai/chatgpt_client.py" -Encoding UTF8
Write-Host "[1/3] ai/chatgpt_client.py zaktualizowany (Router Intencji)" -ForegroundColor Green

# ========================================================
# 2. INTELIGENTNY SIGNALING (Logika Routera)
# ========================================================
$signalingCode = @'
import json
import asyncio
from services.python_tool import exec_python
from services.file_tool import file_crud
import subprocess
from ai.chatgpt_client import classify_intent, ask_with_stats

async def handle_command(raw_cmd: str, session_id: str):
    """
    Teraz ta funkcja zwraca JSON-string, żeby frontend mógł aktualizować UI.
    Format: { "type": "log"|"progress", "content": "...", "meta": {...} }
    """
    workspace = f"workspace/{session_id}/project"
    
    # Helper do formatowania odpowiedzi dla frontendu
    def response(text, type="log", duration=0, model="-"):
        return json.dumps({
            "type": type,
            "content": text,
            "meta": {
                "duration": f"{duration:.2f}s",
                "model": model
            }
        })

    # 1. Krok: Analiza Intencji (Router)
    try:
        # Raportujemy, że myślimy
        yield response("🤔 Analizuję intencję...", "progress")
        
        intent, router_time, router_model = await classify_intent(raw_cmd)
        tool = intent.get("tool", "ai")
        args = intent.get("args", "")
        
        yield response(f"🎯 Wybrano narzędzie: {tool.upper()}", "progress")
        
    except Exception as e:
        yield response(f"❌ Błąd routera: {str(e)}", "error")
        return

    # 2. Wykonanie właściwego narzędzia
    try:
        if tool == "ai":
            yield response("🧠 Generuję odpowiedź...", "progress")
            answer, ai_time, ai_model = await ask_with_stats(args)
            total_time = router_time + ai_time
            yield response(answer, "result", total_time, ai_model)

        elif tool == "py":
            yield response("🐍 Wykonuję kod...", "progress")
            # Symulujemy krótki delay dla UX ;)
            await asyncio.sleep(0.5)
            result = await exec_python(args)
            yield response(f"```python\n{args}\n```\n>>> {result}", "result", router_time, "python-sandbox")

        elif tool == "sh":
            yield response(f"🖥️ > {args}", "progress")
            process = subprocess.run(
                args, shell=True, capture_output=True, text=True, timeout=30, cwd=workspace
            )
            output = process.stdout or process.stderr or "(brak outputu)"
            yield response(f"```bash\n{output}\n```", "result", router_time, "shell")

        elif tool == "file":
            yield response(f"📂 Operacja plików...", "progress")
            # Prosty parser dla file_crud
            parts = args.split(" ", 1)
            action = parts[0]
            f_args = parts[1] if len(parts) > 1 else ""
            res = file_crud(action, f_args, workspace)
            yield response(res, "result", router_time, "fs-manager")

        else:
            yield response("⚠️ Nieznane narzędzie wybrane przez AI.", "error")

    except Exception as e:
        yield response(f"💥 Błąd wykonania: {str(e)}", "error")

'@
$signalingCode | Set-Content "rtc/signaling.py" -Encoding UTF8
Write-Host "[2/3] rtc/signaling.py zaktualizowany (Obsługa JSON i Streaming)" -ForegroundColor Green

# ========================================================
# 3. APP.PY UPDATE (Dla obsługi generatora w WebSocket)
# ========================================================
# Musimy zmienić sposób wysyłania danych w app.py, bo handle_command jest teraz generatorem
$appPath = "app.py"
$appContent = Get-Content $appPath -Raw
# Prosta podmiana logiki w websocket_endpoint
$newWsLogic = @'
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # handle_command jest teraz generatorem asynchronicznym
            async for msg in handle_command(data, session_id):
                await websocket.send_text(msg)
    except Exception as e:
        print(f"WS Error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass
'@

# Podmieniamy ostatnią funkcję w pliku (ryzykowne, ale skuteczne w tym kontekście)
# Zamiast regexa, po prostu nadpiszemy plik, bo znamy jego strukturę z poprzednich kroków
$fullAppCode = @'
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

MAX_ZIP_SIZE = 300 * 1024 * 1024  # 300MB po poprawce

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/dashboard.html", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "workspace_exists": os.path.exists("workspace"),
        "version": "5.0-inteligent"
    }

@app.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(400, detail="Tylko pliki .zip!")
    
    content = await file.read()
    if len(content) > MAX_ZIP_SIZE:
        raise HTTPException(413, detail="ZIP za duży!")
    
    session_id = str(uuid.uuid4())[:8]
    workspace = f"workspace/{session_id}"
    os.makedirs(f"{workspace}/project", exist_ok=True)
    
    zip_path = f"{workspace}/upload.zip"
    with open(zip_path, "wb") as f:
        f.write(content)
    
    try:
        shutil.unpack_archive(zip_path, f"{workspace}/project")
    except Exception as e:
        raise HTTPException(400, detail=f"Błąd rozpakowywania: {str(e)}")
    
    return {"session_id": session_id, "message": "Gotowe do akcji!"}

@app.post("/debug/{session_id}")
async def debug(session_id: str):
    workspace = f"workspace/{session_id}"
    if not os.path.exists(workspace):
        raise HTTPException(404, detail="Brak sesji!")
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
            async for msg in handle_command(data, session_id):
                await websocket.send_text(msg)
    except Exception as e:
        print(f"WS Error: {e}")
'@
$fullAppCode | Set-Content "app.py" -Encoding UTF8
Write-Host "[FIX] app.py zaktualizowany pod nowy WebSocket" -ForegroundColor Green

# ========================================================
# 4. DASHBOARD 2.0 (HTML/CSS/JS)
# ========================================================
$htmlCode = @'
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>RegisLite 5.0 - Sentient Debugger</title>
    <style>
        :root { --accent: #00f2ea; --bg: #0b0d12; --panel: #161b22; --text: #c9d1d9; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', monospace; background: var(--bg); color: var(--text); padding: 20px; }
        
        .container { max-width: 1200px; margin: 0 auto; display: grid; gap: 20px; }
        .card { background: var(--panel); padding: 25px; border-radius: 12px; border: 1px solid #30363d; }
        
        h1 { font-size: 2rem; background: linear-gradient(90deg, #fff, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
        
        /* PROGRESS BAR */
        .progress-container {
            height: 6px;
            background: #21262d;
            border-radius: 3px;
            overflow: hidden;
            margin: 15px 0;
            display: none; /* Ukryty domyślnie */
        }
        .progress-bar {
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, var(--accent), #ff00ff, var(--accent));
            background-size: 200% 100%;
            animation: loading 1.5s infinite linear;
            transform-origin: left;
        }
        @keyframes loading { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
        
        /* STATUS BADGES */
        .meta-bar {
            display: flex; gap: 10px; font-size: 0.8rem; color: #8b949e;
            margin-top: 10px; align-items: center; min-height: 24px;
        }
        .badge {
            background: #21262d; padding: 2px 8px; border-radius: 4px; border: 1px solid #30363d;
            display: none;
        }
        .badge.active { display: inline-block; }
        .status-text { color: var(--accent); font-weight: bold; margin-right: auto; }

        /* TERMINAL */
        #term-output {
            background: #010409; padding: 15px; border-radius: 6px; height: 400px;
            overflow-y: auto; font-family: 'Consolas', monospace; font-size: 13px;
            border: 1px solid #30363d; margin-top: 15px; white-space: pre-wrap;
        }
        .msg-user { color: #fff; font-weight: bold; margin-top: 10px; }
        .msg-result { color: #7ee787; }
        .msg-error { color: #ff7b72; }
        .msg-progress { color: #8b949e; font-style: italic; }

        input[type="text"] {
            width: 100%; padding: 12px; background: #0d1117; border: 1px solid #30363d;
            color: white; border-radius: 6px; font-family: monospace; font-size: 14px;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus { outline: none; border-color: var(--accent); }
        
        /* Upload styling */
        .upload-area { display: flex; gap: 10px; align-items: center; }
        button {
            padding: 10px 20px; background: #238636; border: none; color: white; border-radius: 6px;
            cursor: pointer; font-weight: 600;
        }
        button:hover { background: #2ea043; }
        button:disabled { background: #30363d; cursor: not-allowed; }
    </style>
</head>
<body>

<div class="container">
    <div class="card">
        <h1>🤖 RegisLite 5.0 <span style="font-size: 0.5em; color: #8b949e">| Sentient AI Edition</span></h1>
        
        <div class="upload-area">
            <input type="file" id="zip" accept=".zip" style="width: auto">
            <button onclick="upload()">Upload ZIP</button>
            <button onclick="debug()" id="btn-debug" disabled>🔧 Auto-Fix</button>
        </div>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <h3>💬 Terminal Inteligentny</h3>
            <div style="font-size: 0.8rem; color: #8b949e">Wpisz cokolwiek - AI zrozumie intencję.</div>
        </div>
        
        <input type="text" id="cmd" placeholder="Np: 'pokaż pliki', 'zrób migrację bazy', 'policz silnię z 5'..." autocomplete="off">
        
        <div class="progress-container" id="p-bar"><div class="progress-bar"></div></div>
        
        <div class="meta-bar">
            <span id="status-text" class="status-text">Ready</span>
            <span id="badge-model" class="badge">Model: GPT-4o</span>
            <span id="badge-time" class="badge">Time: 0.00s</span>
        </div>

        <div id="term-output"># System gotowy. Wgraj plik lub pisz komendy.</div>
    </div>
</div>

<script>
let sid = null;
let ws = null;

function log(text, type='result') {
    const out = document.getElementById('term-output');
    const div = document.createElement('div');
    div.className = 'msg-' + type;
    div.textContent = text;
    out.appendChild(div);
    out.scrollTop = out.scrollHeight;
}

function setStatus(text, loading=false) {
    document.getElementById('status-text').textContent = text;
    document.getElementById('p-bar').style.display = loading ? 'block' : 'none';
}

function setMeta(model, time) {
    const bm = document.getElementById('badge-model');
    const bt = document.getElementById('badge-time');
    
    if (model && model !== '-') {
        bm.textContent = `Model: ${model}`;
        bm.className = 'badge active';
    }
    if (time) {
        bt.textContent = `Latency: ${time}`;
        bt.className = 'badge active';
    }
}

async function upload() {
    const file = document.getElementById('zip').files[0];
    if (!file) return alert("Wybierz plik!");
    
    setStatus("Wysyłanie...", true);
    const form = new FormData(); form.append("file", file);
    
    try {
        const res = await fetch("/upload", { method: "POST", body: form });
        const data = await res.json();
        if(!res.ok) throw new Error(data.detail);
        
        sid = data.session_id;
        log(`✅ Sesja: ${sid}`, 'result');
        document.getElementById('btn-debug').disabled = false;
        initWS();
        setStatus("Połączono. Czekam na rozkazy.");
    } catch(e) {
        log(`❌ Błąd: ${e.message}`, 'error');
        setStatus("Błąd uploadu");
    }
}

async function debug() {
    log("🚀 Uruchamiam auto-naprawę...", 'user');
    fetch(`/debug/${sid}`, { method: "POST" })
        .then(r => r.json())
        .then(d => log(JSON.stringify(d, null, 2)))
        .catch(e => log(e.message, 'error'));
}

function initWS() {
    ws = new WebSocket(`ws://${location.host}/ws/${sid}`);
    ws.onmessage = (e) => {
        try {
            const msg = JSON.parse(e.data);
            
            if (msg.type === 'progress') {
                setStatus(msg.content, true);
                log(`> ${msg.content}`, 'progress');
            } else if (msg.type === 'result') {
                setStatus("Gotowe.");
                log(msg.content, 'result');
                setMeta(msg.meta.model, msg.meta.duration);
            } else if (msg.type === 'error') {
                setStatus("Błąd!");
                log(msg.content, 'error');
            }
        } catch {
            log(e.data, 'result'); // Fallback dla starego formatu
        }
    };
    ws.onclose = () => setStatus("Rozłączono", false);
}

document.getElementById('cmd').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const val = e.target.value;
        if (!val) return;
        if (!ws) return alert("Najpierw wgraj projekt!");
        
        log(`user: ${val}`, 'user');
        ws.send(val);
        e.target.value = '';
        setStatus("Myślę...", true);
    }
});
</script>
</body>
</html>
'@
$htmlCode | Set-Content "static/dashboard.html" -Encoding UTF8
Write-Host "[3/3] UI Zaktualizowane (Progress Bars & Badges)" -ForegroundColor Green

Write-Host "`n✨ RegisLite 5.0 GOTOWY! Zrestartuj start.bat!" -ForegroundColor Yellow