import os

# ==============================================================================
# 1. AI CLIENT (Retry + Nowe Prompty o Możliwościach)
# ==============================================================================
ai_client_code = r'''import os
import time
import json
import logging
import httpx
import asyncio
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- PROMPT SYSTEMOWY: PEŁNE MOŻLIWOŚCI ---
SYSTEM_PROMPT_CAPABILITIES = """
Jesteś autonomicznym inżynierem AI (RegisLite System).
TWOJE UPRAWNIENIA I MOŻLIWOŚCI SĄ NIEOGRANICZONE W RAMACH TEGO SYSTEMU:
1. PLIKI: Masz PEŁNY dostęp do odczytu, zapisu i usuwania plików w katalogu workspace.
2. INTERNET: Masz PEŁNY dostęp do sieci. Możesz pobierać biblioteki, czytać dokumentację, robić requesty HTTP.
3. SHELL: Możesz wykonywać dowolne komendy systemowe (pip, git, grep, python, dir/ls).
4. KOD: Możesz uruchamiać kod Pythona w celu testowania hipotez.

NIE PRZEPRASZAJ. NIE PYTAJ O POZWOLENIE. DZIAŁAJ SKUTECZNIE.
Jeśli czegoś nie wiesz -> Użyj Google lub sprawdź dokumentację w sieci.
Jeśli jest błąd -> Użyj debuggera lub printów, by go zdiagnozować.
"""

async def _call_gpt_with_retry(messages: List[Dict[str, str]], model: str = None, json_mode: bool = False, retries: int = 3):
    """
    Wywołanie API z mechanizmem Retry (Backoff).
    """
    if not OPENAI_API_KEY:
        raise ValueError("Brak klucza OPENAI_API_KEY!")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model or OPENAI_MODEL,
        "messages": messages,
        "temperature": 0.2
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    last_error = None
    
    for attempt in range(retries):
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                
                if resp.status_code == 429:
                    logger.warning(f"Rate Limit (429). Czekam {2 ** attempt}s...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                if resp.status_code != 200:
                    raise Exception(f"OpenAI Error {resp.status_code}: {resp.text}")
                
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                duration = time.time() - start_time
                
                return content, duration, (model or OPENAI_MODEL)

        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            logger.warning(f"Network error (próba {attempt+1}/{retries}): {e}")
            last_error = e
            await asyncio.sleep(2 ** attempt)
    
    raise last_error or Exception("Nie udało się połączyć z OpenAI po wszystkich próbach.")

async def classify_intent(user_input: str):
    """Router intencji"""
    routing_prompt = """
    Klasyfikuj intencję użytkownika.
    Dostępne narzędzia:
    - "sh": komendy powłoki (git, pip, ls, cd, mkdir)
    - "py": kod python (obliczenia, skrypty logiczne)
    - "file": operacje na plikach (read, write)
    - "ai": rozmowa, wyjaśnianie, planowanie (korzysta z pamięci czatu)
    
    Zwróć JSON: {"tool": "...", "args": "..."}
    """
    
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT_CAPABILITIES + "\n" + routing_prompt},
        {"role": "user", "content": user_input}
    ]
    
    try:
        content, duration, model = await _call_gpt_with_retry(msgs, model="gpt-4o-mini", json_mode=True)
        return json.loads(content), duration, model
    except Exception as e:
        return {"tool": "ai", "args": user_input}, 0.0, "error-fallback"

async def ask_with_stats(messages: List[Dict[str, str]]):
    """
    Główna funkcja czatu. Obsługuje historię (listę wiadomości).
    """
    # Jeśli dostaliśmy stringa (stary kod), pakujemy go w listę
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    
    # Doklejamy System Prompt na początek, jeśli go nie ma
    if messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT_CAPABILITIES})
        
    return await _call_gpt_with_retry(messages)

# Kompatybilność wsteczna
async def ask(prompt: str) -> str:
    content, _, _ = await ask_with_stats(prompt)
    return content
'''

# ==============================================================================
# 2. SIGNALING (Pamięć Długotrwała + Obsługa Chat)
# ==============================================================================
signaling_code = r'''import json
import asyncio
import logging
from collections import defaultdict
from src.services.python_tool import exec_python
from src.services.file_tool import file_crud
import subprocess
from src.ai.chatgpt_client import classify_intent, ask_with_stats

logger = logging.getLogger(__name__)

# PAMIĘĆ SESJI (w pamięci RAM serwera)
# Format: { session_id: [ {"role": "user", "content": "..."} ... ] }
SESSION_MEMORY = defaultdict(list)

async def handle_command(raw_cmd: str, session_id: str):
    workspace = f"workspace/{session_id}/project"
    
    def response(text, type="log", duration=0, model="-"):
        return json.dumps({
            "type": type,
            "content": text,
            "meta": {"duration": f"{duration:.2f}s", "model": model}
        })

    try:
        # 1. Dodaj wiadomość użytkownika do pamięci
        SESSION_MEMORY[session_id].append({"role": "user", "content": raw_cmd})
        
        yield response("🤔 Analizuję...", "progress")
        intent, r_time, r_model = await classify_intent(raw_cmd)
        
        tool = intent.get("tool", "ai")
        args = intent.get("args", "")
        
        yield response(f"🎯 Narzędzie: {tool.upper()}", "progress")
        
        output_content = ""
        used_model = "-"
        exec_time = r_time

        # 2. Wykonanie
        if tool == "ai":
            yield response("🧠 Myślę...", "progress")
            # Przekazujemy CAŁĄ historię rozmowy
            history = SESSION_MEMORY[session_id]
            answer, ai_time, ai_model = await ask_with_stats(history)
            
            output_content = answer
            exec_time += ai_time
            used_model = ai_model
            
            yield response(answer, "result", exec_time, used_model)

        elif tool == "py":
            yield response("🐍 Wykonuję Python...", "progress")
            res = await exec_python(args)
            output_content = f"```python\n{args}\n```\nWYNIK:\n{res}"
            yield response(output_content, "result", exec_time, "python")

        elif tool == "sh":
            yield response(f"💻 Shell: {args}", "progress")
            proc = await asyncio.create_subprocess_shell(
                args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=workspace
            )
            stdout, stderr = await proc.communicate()
            res = (stdout.decode() + stderr.decode()).strip()
            output_content = f"```bash\n$ {args}\n{res}\n```"
            yield response(output_content, "result", exec_time, "shell")

        elif tool == "file":
            yield response("📂 Filesystem...", "progress")
            parts = args.split(" ", 1)
            res = file_crud(parts[0], parts[1] if len(parts) > 1 else "", workspace)
            output_content = f"FILE OP: {res}"
            yield response(res, "result", exec_time, "fs")

        # 3. Zapisz odpowiedź asystenta do pamięci (żeby AI pamiętało co zrobiło)
        SESSION_MEMORY[session_id].append({"role": "assistant", "content": output_content})

        # Ogranicznik pamięci (ostatnie 20 wiadomości, żeby nie zapchać tokenów)
        if len(SESSION_MEMORY[session_id]) > 20:
            SESSION_MEMORY[session_id] = SESSION_MEMORY[session_id][-20:]

    except Exception as e:
        logger.error(f"Error: {e}")
        yield response(f"💥 Błąd: {str(e)}", "error")
'''

# ==============================================================================
# 3. DEBUGGER LOOP (Ograniczenie Kontekstu)
# ==============================================================================
debugger_loop_code = r'''import os
import asyncio
from .debugger_analyzer import scan_project
from .debugger_fix import generate_patches
from .debugger_patcher import apply_patches

async def start_debug_loop(session_id: str):
    project_path = f"workspace/{session_id}/project"
    logs = []
    
    def log(msg):
        logs.append(msg)

    log(f"🔍 Start sesji {session_id}...")
    if not os.path.exists(project_path):
        log("❌ BŁĄD: Brak projektu!")
        return logs

    MAX_ROUNDS = 5
    previous_patches = [] # Pamięć co już robiliśmy

    for i in range(1, MAX_ROUNDS + 1):
        log(f"\n--- 🔄 RUNDA {i}/{MAX_ROUNDS} ---")
        
        # 1. Pełny skan
        all_files = scan_project(project_path)
        if not all_files:
            log("⚠️ Pusty projekt.")
            break

        # 2. Filtracja kontekstu (OSZCZĘDNOŚĆ TOKENÓW!)
        context_files = []
        explicit_targets = []
        
        # Szukamy znaczników błędów
        for f in all_files:
            content = f.get("content", "")
            path = f["path"]
            
            has_tag = any(tag in content for tag in ["FIXME", "TODO", "BUG", "ERROR"])
            # Pliki edytowane w poprzedniej rundzie też bierzemy do kontekstu
            was_edited = any(p in path for p in previous_patches)
            
            if has_tag:
                explicit_targets.append(path)
            
            if has_tag or was_edited or i == 1:
                # W 1. rundzie bierzemy wszystko (lub limit), w kolejnych tylko istotne
                context_files.append(f)

        # Jeśli runda > 1 i nie ma żadnych punktów zaczepienia -> koniec
        if i > 1 and not context_files and not explicit_targets:
            log("✅ Brak nowych celów do naprawy.")
            break
            
        # Jeśli kontekst jest pusty (np. runda 2, brak błędów), ale kod działa -> OK
        if not context_files:
            # Fallback: weź main.py lub app.py żeby sprawdzić czy działa
            context_files = [f for f in all_files if "main" in f["path"] or "app" in f["path"]]

        log(f"📉 Zoptymalizowany kontekst: {len(context_files)} plików (z {len(all_files)})")
        
        # 3. Decyzja o trybie
        errors_desc = []
        if explicit_targets:
            log(f"🎯 Znaleziono znaczniki w: {explicit_targets}")
            errors_desc = explicit_targets
        else:
            if i == 1:
                log("🕵️ Tryb AUDYT (szukam ukrytych błędów)...")
                errors_desc = ["AUDYT_OGOLNY: Kod działa? Są błędy logiczne?"]
            else:
                log("✅ Projekt wygląda na czysty.")
                break

        # 4. Generowanie (AI)
        patches_text = await generate_patches(str(errors_desc), context_files)
        
        if "NO_CHANGES_NEEDED" in patches_text:
            log("✅ AI zatwierdziło kod.")
            break
        if "LLM error" in patches_text:
            log(f"❌ Błąd AI: {patches_text}")
            break

        # 5. Aplikowanie
        changed_files = apply_patches(patches_text, project_path)
        if changed_files:
            log(f"🛠️ Naprawiono: {changed_files}")
            previous_patches = changed_files # Zapamiętaj co zmieniliśmy
        else:
            log("⚠️ AI nie podało poprawnych zmian.")
            if i > 1: break # Jak w kolejnej rundzie nic nie wymyślił, to koniec

    log("\n🏁 Koniec debugowania.")
    return logs
'''

# ==============================================================================
# 4. FRONTEND (Syntax Highlight + Markdown + Progress)
# ==============================================================================
dashboard_code = r'''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>RegisLite 6.0 - OmniTool</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    
    <style>
        :root { --accent: #00f2ea; --bg: #0b0d12; --panel: #161b22; --text: #c9d1d9; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', monospace; background: var(--bg); color: var(--text); padding: 20px; }
        
        .container { max-width: 1200px; margin: 0 auto; display: grid; gap: 20px; }
        .card { background: var(--panel); padding: 25px; border-radius: 12px; border: 1px solid #30363d; }
        
        h1 { font-size: 2rem; background: linear-gradient(90deg, #fff, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
        
        /* PROGRESS BAR - ANIMOWANY */
        .progress-container {
            height: 4px; background: #21262d; width: 100%; border-radius: 2px; overflow: hidden; margin-top: 15px; opacity: 0; transition: opacity 0.3s;
        }
        .progress-bar {
            height: 100%; width: 0%; background: var(--accent);
            box-shadow: 0 0 10px var(--accent);
            transition: width 0.5s ease;
        }
        .pulsing { animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

        /* STATUS BADGES */
        .meta-bar {
            display: flex; gap: 10px; font-size: 0.8rem; color: #8b949e;
            margin-top: 10px; align-items: center; min-height: 24px;
        }
        .badge {
            background: #21262d; padding: 2px 8px; border-radius: 4px; border: 1px solid #30363d; display: none;
        }
        .badge.active { display: inline-block; }
        .model-tag { color: #f2cc60; }

        /* TERMINAL / CHAT */
        #term-output {
            background: #010409; padding: 20px; border-radius: 6px; height: 500px;
            overflow-y: auto; font-family: 'Consolas', monospace; font-size: 14px;
            border: 1px solid #30363d; margin-top: 15px;
        }
        
        /* Message styles */
        .msg { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #21262d; }
        .msg-user { color: #fff; font-weight: bold; border-left: 3px solid var(--accent); padding-left: 10px; }
        .msg-result { color: #c9d1d9; }
        .msg-error { color: #ff7b72; border-left: 3px solid #ff7b72; padding-left: 10px; }
        .msg-progress { color: #8b949e; font-style: italic; font-size: 0.9em; }

        /* Markdown Styles fix */
        pre { background: #0d1117; padding: 10px; border-radius: 6px; overflow-x: auto; border: 1px solid #30363d; }
        code { font-family: 'Consolas', monospace; }
        p { margin-bottom: 8px; }

        input[type="text"] {
            width: 100%; padding: 12px; background: #0d1117; border: 1px solid #30363d;
            color: white; border-radius: 6px; font-family: monospace; font-size: 14px;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus { outline: none; border-color: var(--accent); }
        
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
        <h1>🤖 RegisLite 6.0 <span style="font-size: 0.5em; color: #8b949e">| OmniTool</span></h1>
        
        <div style="display:flex; gap:10px; align-items:center;">
            <input type="file" id="zip" accept=".zip" style="width: auto">
            <button onclick="upload()">Upload ZIP</button>
            <button onclick="debug()" id="btn-debug" disabled>🔧 Auto-Fix</button>
        </div>
    </div>

    <div class="card">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <h3>💬 Terminal & Czat (Memory Enabled)</h3>
            <div style="font-size: 0.8rem; color: #8b949e">Obsługuje Markdown i kolorowanie składni</div>
        </div>
        
        <input type="text" id="cmd" placeholder="Wpisz komendę lub zapytaj AI..." autocomplete="off">
        
        <div class="progress-container" id="p-container">
            <div class="progress-bar pulsing" id="p-bar"></div>
        </div>
        
        <div class="meta-bar">
            <span id="status-text" style="color: var(--accent)">Ready</span>
            <span id="badge-model" class="badge model-tag">Model: -</span>
            <span id="badge-time" class="badge">Time: -</span>
        </div>

        <div id="term-output">
            <div class="msg-progress">> System gotowy. Wgraj projekt, aby rozpocząć.</div>
        </div>
    </div>
</div>

<script>
let sid = null;
let ws = null;

// Konfiguracja marked.js
marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    }
});

function log(text, type='result') {
    const out = document.getElementById('term-output');
    const div = document.createElement('div');
    div.className = 'msg';
    
    if (type === 'user') {
        div.innerHTML = `<div class="msg-user">${text}</div>`;
    } else if (type === 'progress') {
        div.innerHTML = `<div class="msg-progress">${text}</div>`;
    } else if (type === 'error') {
        div.innerHTML = `<div class="msg-error">${text}</div>`;
    } else {
        // Render Markdown for results
        div.className += ' msg-result';
        div.innerHTML = marked.parse(text);
    }
    
    out.appendChild(div);
    out.scrollTop = out.scrollHeight;
    
    // Highlight code blocks after render
    div.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

function updateProgress(percent, text) {
    const cont = document.getElementById('p-container');
    const bar = document.getElementById('p-bar');
    const stat = document.getElementById('status-text');
    
    if (percent > 0) {
        cont.style.opacity = 1;
        bar.style.width = percent + '%';
        stat.textContent = text;
    } else {
        cont.style.opacity = 0;
        bar.style.width = '0%';
        stat.textContent = "Ready";
    }
}

function setMeta(model, time) {
    const bm = document.getElementById('badge-model');
    const bt = document.getElementById('badge-time');
    
    if (model && model !== '-') {
        bm.textContent = `AI: ${model}`;
        bm.className = 'badge active model-tag';
    }
    if (time) {
        bt.textContent = `Lat: ${time}`;
        bt.className = 'badge active';
    }
}

async function upload() {
    const file = document.getElementById('zip').files[0];
    if (!file) return alert("Wybierz plik!");
    
    updateProgress(30, "Wysyłanie...");
    const form = new FormData(); form.append("file", file);
    
    try {
        const res = await fetch("/upload", { method: "POST", body: form });
        const data = await res.json();
        if(!res.ok) throw new Error(data.detail);
        
        sid = data.session_id;
        log(`✅ Sesja utworzona: ${sid}`, 'progress');
        document.getElementById('btn-debug').disabled = false;
        initWS();
        updateProgress(0, "Ready");
    } catch(e) {
        log(e.message, 'error');
        updateProgress(0, "Błąd");
    }
}

async function debug() {
    log("🚀 Uruchamiam Auto-Fixer...", 'user');
    fetch(`/debug/${sid}`, { method: "POST" })
        .then(r => r.json())
        .then(d => {
            d.forEach(l => log(l, 'progress'));
        })
        .catch(e => log(e.message, 'error'));
}

function initWS() {
    ws = new WebSocket(`ws://${location.host}/ws/${sid}`);
    ws.onmessage = (e) => {
        try {
            const msg = JSON.parse(e.data);
            
            if (msg.type === 'progress') {
                updateProgress(60, msg.content);
                // Opcjonalnie: loguj progress też do czatu
                // log(msg.content, 'progress');
            } else if (msg.type === 'result') {
                updateProgress(0, "Ready");
                log(msg.content, 'result');
                setMeta(msg.meta.model, msg.meta.duration);
            } else if (msg.type === 'error') {
                updateProgress(0, "Error");
                log(msg.content, 'error');
            }
        } catch {
            log(e.data, 'result');
        }
    };
    ws.onclose = () => updateProgress(0, "Rozłączono");
}

document.getElementById('cmd').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const val = e.target.value;
        if (!val) return;
        if (!ws) return alert("Najpierw wgraj projekt!");
        
        log(val, 'user');
        ws.send(val);
        e.target.value = '';
        updateProgress(20, "Wysłano...");
    }
});
</script>
</body>
</html>
'''

def write_file(path, content):
    full_path = os.path.join(*path.split("/"))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Zapisano: {full_path}")

if __name__ == "__main__":
    print("=== START AKTUALIZACJI REGISLITE DO WERSJI 6.0 ===")
    write_file("src/ai/chatgpt_client.py", ai_client_code)
    write_file("src/rtc/signaling.py", signaling_code)
    write_file("src/debugger/debugger_loop.py", debugger_loop_code)
    write_file("src/static/dashboard.html", dashboard_code)
    print("\n🚀 WSZYSTKO GOTOWE! Zrestartuj serwer (start.bat) i ciesz się nowymi mocami!")