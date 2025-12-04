# ==========================================
#     REGISLITE TOTAL REPAIR SCRIPT 🔧
#     Usuwa duplikaty, poprawia importy, naprawia wszystko!
#     Data: 04.12.2025
# ==========================================

Clear-Host
Write-Host "`n" -NoNewline
Write-Host "  ██████╗ ███████╗██████╗  █████╗ ██╗██████╗ " -ForegroundColor Red
Write-Host "  ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║██╔══██╗" -ForegroundColor Red
Write-Host "  ██████╔╝█████╗  ██████╔╝███████║██║██████╔╝" -ForegroundColor Red
Write-Host "  ██╔══██╗██╔══╝  ██╔═══╝ ██╔══██║██║██╔══██╗" -ForegroundColor Red
Write-Host "  ██║  ██║███████╗██║     ██║  ██║██║██║  ██║" -ForegroundColor Red
Write-Host "  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝" -ForegroundColor Red
Write-Host "`n          NAPRAWIAMY REGISLITE - TOTALNY REMONT!`n" -ForegroundColor Yellow

Set-Location (Split-Path $MyInvocation.MyCommand.Path)

# ==========================================
# KROK 1: USUŃ DUPLIKATY
# ==========================================
Write-Host "[1/5] Usuwam duplikaty plików..." -ForegroundColor Cyan

$duplicates = @(
    "debugger\analyzer.py",
    "debugger\fix.py",
    "debugger\patcher.py",
    "debugger\loop.py",
    "debugger\chatgpt_client.py",
    "static\index.html"
)

foreach ($file in $duplicates) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Usunięto: $file" -ForegroundColor Green
    }
}

Write-Host "`n[✓] Duplikaty usunięte!`n" -ForegroundColor Green

# ==========================================
# KROK 2: POPRAW IMPORTY W APP.PY
# ==========================================
Write-Host "[2/5] Poprawiam importy w app.py..." -ForegroundColor Cyan

$appContent = @'
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
'@

$appContent | Out-File -Encoding utf8 "app.py"
Write-Host "  ✓ app.py zaktualizowany" -ForegroundColor Green

# ==========================================
# KROK 3: POPRAW SIGNALING.PY
# ==========================================
Write-Host "`n[3/5] Poprawiam rtc/signaling.py..." -ForegroundColor Cyan

$signalingContent = @'
# rtc/signaling.py - FIXED VERSION
import asyncio
from services.python_tool import exec_python
from services.file_tool import file_crud
import subprocess
from ai.chatgpt_client import ask

async def handle_command(cmd: str, session_id: str):
    """
    Obsługuje komendy z terminala WebSocket:
    - ai:prompt → zapytanie do ChatGPT
    - py:code → wykonanie kodu Python
    - sh:command → wykonanie komendy shell
    - file:action args → operacje na plikach
    """
    if cmd.startswith("ai:"):
        prompt = cmd[3:].strip()
        response = await ask(prompt)
        return f"AI: {response}"
    
    elif cmd.startswith("py:"):
        code = cmd[3:].strip()
        result = await exec_python(code)
        return f"Python: {result}"
    
    elif cmd.startswith("sh:"):
        shell_cmd = cmd[3:].strip()
        try:
            result = subprocess.run(
                shell_cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return f"Shell: {result.stdout or result.stderr}"
        except subprocess.TimeoutExpired:
            return "Shell: [ERROR] Timeout - komenda trwała za długo"
        except Exception as e:
            return f"Shell: [ERROR] {str(e)}"
    
    elif cmd.startswith("file:"):
        parts = cmd[5:].split(" ", 1)
        action = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        workspace = f"workspace/{session_id}/project"
        result = file_crud(action, args, workspace)
        return f"File: {result}"
    
    else:
        return "❌ Nieznana komenda! Użyj: ai: / py: / sh: / file:"
'@

$signalingContent | Out-File -Encoding utf8 "rtc\signaling.py"
Write-Host "  ✓ rtc/signaling.py zaktualizowany" -ForegroundColor Green

# ==========================================
# KROK 4: POPRAW DASHBOARD.HTML
# ==========================================
Write-Host "`n[4/5] Poprawiam static/dashboard.html..." -ForegroundColor Cyan

$dashboardContent = @'
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>RegisLite 4.5 – Polski AI Debugger</title>
    <script src="https://unpkg.com/simple-peer@9.11.1/simplepeer.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: linear-gradient(135deg, #0d1117 0%, #1a1e2e 100%); 
            color: #c9d1d9; 
            padding: 20px; 
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { 
            background: #161b22; 
            padding: 40px; 
            border-radius: 16px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
            margin-bottom: 20px;
        }
        h1 { 
            color: #58a6ff; 
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        }
        .subtitle {
            color: #8b949e;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-left: 10px;
        }
        .status-ready { background: #238636; color: white; }
        .status-working { background: #d29922; color: white; }
        .status-error { background: #da3633; color: white; }
        
        button { 
            padding: 14px 28px; 
            font-size: 18px; 
            background: #238636; 
            border: none; 
            border-radius: 8px; 
            color: white; 
            cursor: pointer; 
            margin: 10px 10px 10px 0; 
            transition: all 0.3s;
            font-weight: 600;
        }
        button:hover { 
            background: #2ea043; 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(35, 134, 54, 0.4);
        }
        button:disabled { 
            background: #555; 
            cursor: not-allowed;
            transform: none;
        }
        
        #logs { 
            background: #010409; 
            padding: 20px; 
            border-radius: 8px; 
            white-space: pre-wrap; 
            margin-top: 20px; 
            min-height: 300px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.6;
            overflow-y: auto;
            max-height: 500px;
            border: 1px solid #30363d;
        }
        
        #terminal { 
            background: #0d1117; 
            padding: 20px; 
            border: 2px solid #58a6ff; 
            border-radius: 8px; 
            margin-top: 20px; 
        }
        .terminal-header {
            color: #58a6ff;
            font-weight: 600;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        #cmd { 
            width: calc(100% - 120px); 
            padding: 12px; 
            background: #30363d; 
            border: 1px solid #58a6ff; 
            color: white;
            border-radius: 6px;
            font-family: 'Consolas', monospace;
            font-size: 14px;
        }
        #term-output {
            margin-top: 15px;
            padding: 15px;
            background: #010409;
            border-radius: 6px;
            min-height: 200px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            color: #0f0;
            max-height: 400px;
            overflow-y: auto;
        }
        
        input[type="file"] { 
            padding: 12px; 
            background: #30363d; 
            border: 2px solid #58a6ff; 
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }
        input[type="file"]::file-selector-button {
            background: #238636;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            color: white;
            cursor: pointer;
            margin-right: 10px;
        }
        
        .emoji { font-size: 1.5rem; margin-right: 8px; }
        .section-title {
            color: #58a6ff;
            font-size: 1.3rem;
            margin-bottom: 15px;
            font-weight: 600;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h1><span class="emoji">🤖</span>RegisLite v4.5 <span class="status-badge status-ready" id="status">READY</span></h1>
        <p class="subtitle">Polski AI Debugger - Upload → Analyze → Fix → Deploy</p>
        
        <div class="section-title"><span class="emoji">📦</span>1. Wybierz projekt</div>
        <input type="file" id="zip" accept=".zip">
        <button onclick="upload()">Upload ZIP</button>
        <button onclick="debug()" id="btn" disabled>🚀 Start Debug</button>
        
        <div class="section-title" style="margin-top: 30px;"><span class="emoji">📊</span>2. Logi debugowania</div>
        <div id="logs">Gotowy do pracy... Czekam na ZIP! 🥟</div>
    </div>
    
    <div class="card">
        <div class="terminal-header"><span class="emoji">💻</span>Terminal Interaktywny</div>
        <p style="color: #8b949e; margin-bottom: 15px;">
            Komendy: <code>ai:prompt</code>, <code>py:code</code>, <code>sh:command</code>, <code>file:action path</code>
        </p>
        <input type="text" id="cmd" placeholder="Wpisz komendę... np: ai:napisz funkcję sortującą">
        <button onclick="sendCmd()">Wyślij</button>
        <div id="term-output"># Terminal gotowy...\n# Wpisz komendę powyżej i kliknij Wyślij</div>
    </div>
</div>

<script>
let sid = null;
let ws = null;

function updateStatus(text, type) {
    const badge = document.getElementById('status');
    badge.textContent = text;
    badge.className = 'status-badge status-' + type;
}

async function upload() {
    const file = document.getElementById('zip').files[0];
    if (!file) {
        alert("Wybierz ZIP!");
        return;
    }
    
    updateStatus('UPLOADING...', 'working');
    log(`📤 Wysyłam: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
    
    const form = new FormData();
    form.append("file", file);
    
    try {
        const res = await fetch("/upload", { method: "POST", body: form });
        
        if (!res.ok) {
            const error = await res.json();
            log(`❌ BŁĄD: ${error.detail}`);
            updateStatus('ERROR', 'error');
            return;
        }
        
        const data = await res.json();
        sid = data.session_id;
        log(`✅ Session: ${sid}\n${data.message}`);
        document.getElementById('btn').disabled = false;
        updateStatus('READY TO DEBUG', 'ready');
        initWebSocket();
    } catch (err) {
        log(`❌ BŁĄD POŁĄCZENIA: ${err.message}`);
        updateStatus('ERROR', 'error');
    }
}

async function debug() {
    if (!sid) {
        alert("Najpierw wgraj ZIP!");
        return;
    }
    
    updateStatus('DEBUGGING...', 'working');
    log(`\n🔍 Rozpoczynam debugowanie sesji ${sid}...\n`);
    document.getElementById('btn').disabled = true;
    
    try {
        const res = await fetch(`/debug/${sid}`, { method: "POST" });
        const data = await res.json();
        
        if (data.logs) {
            log(Array.isArray(data.logs) ? data.logs.join('\n') : data.logs);
        } else {
            log(JSON.stringify(data, null, 2));
        }
        
        updateStatus('DEBUG COMPLETE', 'ready');
        document.getElementById('btn').disabled = false;
    } catch (err) {
        log(`❌ BŁĄD DEBUGOWANIA: ${err.message}`);
        updateStatus('ERROR', 'error');
        document.getElementById('btn').disabled = false;
    }
}

function log(text) {
    const logs = document.getElementById('logs');
    const timestamp = new Date().toLocaleTimeString('pl-PL');
    logs.textContent += `[${timestamp}] ${text}\n`;
    logs.scrollTop = logs.scrollHeight;
}

function initWebSocket() {
    // FIX: Używaj prawidłowego protokołu
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${location.host}/ws/${sid}`;
    
    log(`🔌 Łączę WebSocket: ${wsUrl}`);
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        log("✅ WebSocket połączony!");
        termLog("# WebSocket connected! Ready for commands.");
    };
    
    ws.onmessage = e => {
        termLog(e.data);
    };
    
    ws.onerror = (err) => {
        log(`❌ WebSocket error: ${err}`);
        termLog("# ERROR: WebSocket connection failed!");
    };
    
    ws.onclose = () => {
        log("🔌 WebSocket zamknięty");
        termLog("# WebSocket disconnected.");
    };
}

function termLog(text) {
    document.getElementById('term-output').textContent += '\n' + text;
    document.getElementById('term-output').scrollTop = 
        document.getElementById('term-output').scrollHeight;
}

function sendCmd() {
    const cmd = document.getElementById('cmd').value.trim();
    if (!cmd) return;
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        termLog("# ERROR: WebSocket not connected!");
        return;
    }
    
    termLog(`\n> ${cmd}`);
    ws.send(cmd);
    document.getElementById('cmd').value = "";
}

// Enter w terminalu
document.getElementById('cmd').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendCmd();
});

// Sprawdź health przy załadowaniu
window.addEventListener('load', async () => {
    try {
        const res = await fetch('/health');
        const health = await res.json();
        log(`🏥 Health check: ${health.status}`);
        log(`   OpenAI: ${health.openai_configured ? '✅' : '❌'}`);
        log(`   Workspace: ${health.workspace_exists ? '✅' : '❌'}`);
    } catch (err) {
        log(`⚠️  Health check failed: ${err.message}`);
    }
});
</script>
</body>
</html>
'@

$dashboardContent | Out-File -Encoding utf8 "static\dashboard.html"
Write-Host "  ✓ static/dashboard.html zaktualizowany" -ForegroundColor Green

# ==========================================
# KROK 5: DODAJ .ENV.EXAMPLE
# ==========================================
Write-Host "`n[5/5] Tworzę pliki konfiguracyjne..." -ForegroundColor Cyan

$envExample = @'
# RegisLite Configuration
# Skopiuj ten plik jako .env i uzupełnij wartości

# OpenAI API Key (WYMAGANE)
OPENAI_API_KEY=sk-proj-your-key-here

# Debug mode
DEBUG=True

# Maksymalna liczba iteracji debuggera
MAX_ITERATIONS=10

# Model OpenAI (gpt-4o-mini, gpt-4.1, o3-mini)
OPENAI_MODEL=gpt-4o-mini
'@

$envExample | Out-File -Encoding utf8 ".env.example"
Write-Host "  ✓ .env.example utworzony" -ForegroundColor Green

# ==========================================
# FINALIZACJA
# ==========================================
Write-Host "`n" -NoNewline
Write-Host "════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✨ REGISLITE NAPRAWIONY! ✨" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Green

Write-Host "`nCo zostało zrobione:" -ForegroundColor Yellow
Write-Host "  ✅ Usunięto 6 duplikatów plików" -ForegroundColor White
Write-Host "  ✅ Poprawiono importy w app.py" -ForegroundColor White
Write-Host "  ✅ Naprawiono WebSocket URL" -ForegroundColor White
Write-Host "  ✅ Dodano healthcheck endpoint" -ForegroundColor White
Write-Host "  ✅ Dodano walidację upload" -ForegroundColor White
Write-Host "  ✅ Ulepszono dashboard.html" -ForegroundColor White
Write-Host "  ✅ Utworzono .env.example" -ForegroundColor White

Write-Host "`nNastępne kroki:" -ForegroundColor Yellow
Write-Host "  1. Skopiuj .env.example jako .env" -ForegroundColor Cyan
Write-Host "  2. Uzupełnij OPENAI_API_KEY w .env" -ForegroundColor Cyan
Write-Host "  3. Uruchom: .\run.ps1" -ForegroundColor Cyan
Write-Host "  4. Testuj na http://localhost:8000" -ForegroundColor Cyan

Write-Host "`n🥟 Teraz zasłużone pierogi! 🥟`n" -ForegroundColor Magenta